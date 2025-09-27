import asyncio
import datetime
import hashlib
import random
import re

from findmy import KeyPair
from findmy.reports import AsyncAppleAccount, LocalAnisetteProvider

from const import COLOR_REGEX_STR, CONFIG
from database import Database
from database.models import Accessory, Location, User, BatteryLevel
from database.exceptions import LocationExists

from FindMy.exceptions import WrongColorFormat, NotBase64

COLOR_REGEX = re.compile(COLOR_REGEX_STR)


class FindMy:
    UPDATE_INTERVAL_MIN = 40
    UPDATE_INTERVAL_MAX = 80

    def __init__(self):
        self.account = AsyncAppleAccount.from_json(
            CONFIG.findmy.account, anisette_libs_path=CONFIG.findmy.libs_path
        )
        self.update_task = None
        self.db = Database()

    async def _ensure_admin(self, admin_user_name: str, admin_pwd: str) -> None:
        admin_user = await self.db.get_user(admin_user_name)
        if not admin_user:
            await self.db.add_user(admin_user_name, admin_pwd, is_admin=True)
        else:
            await self.db.update_password(admin_user, admin_pwd)
            admin_user.admin = True
            await self.db.update_user(admin_user)

    async def _hash_report(
        self, accessory_key: str, lat: float, lon: float, timestamp: datetime.datetime
    ) -> str:
        return hashlib.sha256(
            f"{accessory_key}-{lat}-{lon}-{timestamp.timestamp()}".encode("ascii")
        ).hexdigest()

    async def _update_timer(self, hours=2):
        while True:
            await asyncio.sleep(
                random.randint(self.UPDATE_INTERVAL_MAX, self.UPDATE_INTERVAL_MAX)
            )
            await self._refetch_reports(hours=hours)

    async def _refetch_reports(self):
        for user in await self.db.get_users():
            accessories = await self.db.get_accessories_by_user(user=user)
            locations = await self._fetch_locations(accessories)
            for accessory_key in locations:
                for location in locations[accessory_key]:
                    try:
                        await self.db.add_location(location)
                    except LocationExists:
                        pass

    async def _fetch_locations(
        self, accessories: list[Accessory]
    ) -> dict[str, list[Location]]:
        key_pair_map = dict()
        for accessory in accessories:
            key_pair = KeyPair.from_b64(accessory.private_key)
            key_pair_map[key_pair] = accessory

        location_histories = await self.account.fetch_location_history(
            keys=list(key_pair_map.keys())
        )
        accessory_location_map = dict()
        for key_pair in location_histories:
            accessory = key_pair_map[key_pair]
            reports = location_histories[key_pair]
            accessory_location_map[accessory.private_key] = [
                Location(
                    id=await self._hash_report(
                        accessory.private_key,
                        report.latitude,
                        report.longitude,
                        report.timestamp,
                    ),
                    lat=report.latitude,
                    lon=report.longitude,
                    timestamp=report.timestamp.astimezone(tz=datetime.timezone.utc),
                    battery_level=BatteryLevel.from_status(report.status),
                    status=report.status,
                    confidence=report.confidence,
                    horizontal_accuracy=report.horizontal_accuracy,
                    accessory_key=accessory.private_key,
                )
                for report in reports
            ]
        return accessory_location_map

    async def setup(self) -> None:
        await self.db.setup()
        await self._ensure_admin(CONFIG.admin.name, CONFIG.admin.password)
        await self._refetch_reports()
        self.update_task = asyncio.create_task(
            self._update_timer(), name="Location updater"
        )

    async def shutdown(self) -> None:
        await self.account.close()
        await self.db.shutdown()

    async def gen_private_key(self) -> KeyPair:
        return KeyPair.new()

    async def get_locations(
        self,
        accessory: Accessory,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        limit: int | None = None,
    ) -> list[Location]:
        return await self.db.get_locations(
            accessory=accessory, start_date=start_date, end_date=end_date, limit=limit
        )

    async def create_accessory(
        self,
        user: User,
        name: str,
        color: str,
        icon: str,
        private_key_b64: str | None = None,
    ) -> Accessory:
        if not private_key_b64:
            private_key = KeyPair.new()
        else:
            try:
                private_key = KeyPair.from_b64(private_key_b64)
            except:
                raise NotBase64("Provided key can't be decoded from base64.")

        if not COLOR_REGEX.match(color):
            raise WrongColorFormat(
                "Color not a HEX triplet see: https://en.wikipedia.org/wiki/Web_colors#Hex_triplet"
            )

        new_accessory = Accessory(
            private_key=private_key.private_key_b64,
            name=name,
            color=color,
            icon=icon,
            user_id=user.id,
        )
        accessory = await self.db.add_accessory(new_accessory)
        return accessory

    async def update_accessory(
        self,
        user: User,
        name: str,
        color: str,
        icon: str,
        private_key_b64: str | None = None,
    ) -> Accessory:
        try:
            private_key = KeyPair.from_b64(private_key_b64)
        except:
            raise NotBase64("Provided key can't be decoded from base64.")

        if not COLOR_REGEX.match(color):
            raise WrongColorFormat(
                "Color not a HEX triplet see: https://en.wikipedia.org/wiki/Web_colors#Hex_triplet"
            )

        new_accessory = Accessory(
            private_key=private_key.private_key_b64,
            name=name,
            color=color,
            icon=icon,
            user_id=user.id,
        )
        accessory = await self.db.update_accessory(user, new_accessory)
        return accessory

    async def remove_accessory(self, user: User, name: str) -> bool:
        accessory = await self.db.get_accessory(user, name)

        if not accessory:
            return False

        await self.db.remove_accessory(accessory)
        return True

    async def get_key_pair_by_name(self, user: User, name: str) -> KeyPair | None:
        accessory = await self.db.get_accessory(user, name)

        if not accessory:
            return None

        return KeyPair.from_b64(accessory.private_key)
