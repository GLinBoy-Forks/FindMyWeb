import asyncio
import datetime
import hashlib
import os
import random
import re
import tomllib

from findmy import KeyPair
from findmy.reports import AsyncAppleAccount, RemoteAnisetteProvider

from const import COLOR_REGEX_STR, CONFIG
from database import Database
from database.models import Accessory, Location, User

COLOR_REGEX = re.compile(COLOR_REGEX_STR)


class WrongColorFormat(Exception):
    """Raised when the color for an `Accessory` doesn't use the HTML color format"""


class FindMy:
    UPDATE_INTERVAL = 60

    def __init__(self):
        self.anisette = RemoteAnisetteProvider(CONFIG.findmy.anisette)
        self.account = AsyncAppleAccount(anisette=self.anisette)
        self.account.from_json(CONFIG.findmy.account)
        self.update_task = None
        self.db = Database()

    async def _ensure_admin(self, admin_user_name: str, admin_pwd: str) -> None:
        admin_user = await self.db.get_user(admin_user_name)
        if not admin_user:
            await self.db.add_user(admin_user, admin_pwd, is_admin=True)
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

    async def _update_timer(self):
        while True:
            await asyncio.sleep(self.UPDATE_INTERVAL)
            await self._refetch_reports()

    async def _refetch_reports(self):
        for user in await self.db.get_users():
            accessories = await self.db.get_accessories_by_user(user=user)
            for accessory in accessories:
                locations = await self._fetch_locations(accessory)
                for location in locations:
                    await self.db.add_location(location)

    async def _fetch_locations(
        self, accessory: Accessory, hours: int = 7 * 24
    ) -> list[Location]:
        key_pair = KeyPair.from_b64(accessory.private_key)

        reports = await self.account.fetch_last_reports(keys=key_pair, hours=hours)

        return [
            Location(
                id=await self._hash_report(
                    accessory.private_key,
                    report.latitude,
                    report.longitude,
                    report.timestamp,
                ),
                lat=report.latitude,
                lon=report.longitude,
                timestamp=report.timestamp,
                accessory_key=accessory.private_key,
            )
            for report in reports
        ]

    async def setup(self) -> None:
        await self.db.setup()
        await self._ensure_admin(CONFIG.admin.name, CONFIG.admin.password)
        await self._refetch_reports()
        loop = asyncio.get_event_loop()
        self.update_task = loop.create_task(self._update_timer())

    async def gen_private_key(self) -> KeyPair:
        return KeyPair.new()

    async def get_locations(
        self, accessory: Accessory, limit: int | None = None
    ) -> list[Location]:
        return await self.db.get_locations(accessory=accessory, limit=limit)

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
            private_key = KeyPair.from_b64(private_key_b64)

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
        if not private_key_b64:
            private_key = KeyPair.new()
        else:
            private_key = KeyPair.from_b64(private_key_b64)

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
