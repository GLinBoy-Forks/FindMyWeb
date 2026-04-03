import asyncio
import base64
import datetime
import hashlib
import logging
import random
import re
import uuid

from findmy import FindMyAccessory, KeyPair
from findmy.errors import UnhandledProtocolError
from findmy.reports import AsyncAppleAccount
from pydantic_extra_types.coordinate import Latitude, Longitude
from sqlmodel import select

from app.const import COLOR_REGEX_STR, CONFIG
from app.database import Database
from app.database.exceptions import LocationExists
from app.database.models import (
    Accessory,
    FruityTagLocationInfo,
    FruityTagRollingAccessoryInfo,
    FruityTagStaticAccessoryInfo,
    Location,
    User,
)
from app.helpers import UNKNOW_PROVIDER_EXCEPTION
from app.models.accessory import AccessoryOptions
from app.providers.provider import Provider
from app.providers.types import (
    AccessoryProvider,
    AccessoryType,
    BatteryLevel,
    LocationType,
)

COLOR_REGEX = re.compile(COLOR_REGEX_STR)

LOG = logging.getLogger(__name__)


class FruityTag(Provider):
    UPDATE_INTERVAL_MIN = 40
    UPDATE_INTERVAL_MAX = 80

    def __init__(self, db: Database):
        LOG.debug(
            f'Logging in to Apple with account="{CONFIG.findmy.account}" anisette_libs_path="{CONFIG.findmy.libs_path}"'
        )
        self.account = AsyncAppleAccount.from_json(
            CONFIG.findmy.account, anisette_libs_path=CONFIG.findmy.libs_path
        )
        self.update_task = None
        self.db = db

    async def _hash_report(
        self, accessory_key: bytes, lat: float, lon: float, timestamp: datetime.datetime
    ) -> uuid.UUID:
        return uuid.UUID(
            bytes=hashlib.shake_128(
                f"{base64.b64encode(accessory_key)}-{lat}-{lon}-{timestamp.timestamp()}".encode(
                    "ascii"
                )
            ).digest(16)
        )

    async def _update_timer(self, hours=2):
        while True:
            LOG.debug("Fetching new reports")
            try:
                await self._refetch_reports()
            except Exception as ex:
                LOG.error(f"Couldn't Fetch new reports: {ex}")
            await asyncio.sleep(
                random.randint(self.UPDATE_INTERVAL_MAX, self.UPDATE_INTERVAL_MAX)
            )

    async def _refetch_reports(self):
        for user in await self.db.get_users():
            accessories = await self.db.get_accessories_by_user(user=user)
            locations = await self._fetch_locations(accessories)
            if not locations:
                LOG.debug(
                    f"No Locations found for accessories owned by {user.username}"
                )
                continue

            for accessory_key in locations:
                for location, location_info in locations[accessory_key]:
                    try:
                        await self.db.add_location(location)
                        await self.add_location_info(location_info)
                        LOG.debug(
                            f"Added {location.id} to: {user.username}: {'*' * min(len(accessory_key.hex()), 32)}{accessory_key.hex()[32:]}"
                        )
                    except LocationExists:
                        pass
                    except Exception as ex:
                        LOG.error(f"Couldn't add Location {location.id}: {ex}")
                        pass

    async def _battery_level_from_status(self, status: int) -> BatteryLevel:
        val = status >> 6
        if val == 0b00:
            return BatteryLevel.FULL
        elif val == 0b01:
            return BatteryLevel.MEDIUM
        elif val == 0b10:
            return BatteryLevel.LOW
        elif val == 0b11:
            return BatteryLevel.CRITICAL
        else:
            return BatteryLevel.UNKNOWN

    async def _fetch_locations(
        self, accessories: list[Accessory]
    ) -> dict[bytes, list[tuple[Location, FruityTagLocationInfo]]] | None:
        key_pair_map = dict()
        for accessory in accessories:
            if accessory.provider != AccessoryProvider.FRUITYTAG:
                continue
            info = await self.get_accessory_info(accessory=accessory)
            if isinstance(info, FruityTagStaticAccessoryInfo):
                key_pair = KeyPair(info.master_key)
            elif isinstance(info, FruityTagRollingAccessoryInfo):
                key_pair = FindMyAccessory(
                    master_key=info.master_key,
                    skn=info.series_key,
                    sks=info.secondary_key,
                    paired_at=info.paired_at.astimezone(datetime.UTC),
                    alignment_date=(
                        info.alignment_date.astimezone(datetime.UTC)
                        if info.alignment_date
                        else None
                    ),
                    alignment_index=info.alignment_index,
                )
            else:
                LOG.error(f"Unknown accessory info type: {type(info)}")
                continue
            key_pair_map[key_pair] = info

        location_histories = None

        for i in range(5):
            try:
                location_histories = await self.account.fetch_location_history(
                    keys=list(key_pair_map.keys())
                )
                break
            except UnhandledProtocolError:  # TODO: Occurs sometimes
                await asyncio.sleep(
                    random.randint(100, 500) / 1000
                )  # Random time between 100ms and 500ms
        if not location_histories:
            return None

        accessory_location_map = dict()
        for key_pair in location_histories:
            accessory = key_pair_map[key_pair]
            reports = location_histories[key_pair]
            locations = list()
            for report in reports:
                base_location = Location(
                    id=await self._hash_report(
                        accessory.master_key,
                        report.latitude,
                        report.longitude,
                        report.timestamp,
                    ),
                    type=LocationType.FRUITYTAG,
                    lat=Latitude(report.latitude),
                    lon=Longitude(report.longitude),
                    timestamp=report.timestamp.astimezone(tz=datetime.UTC),
                    battery_level=await self._battery_level_from_status(report.status),
                    accessory_id=accessory.id,
                )
                location_info = FruityTagLocationInfo(
                    id=base_location.id,
                    status=report.status,
                    confidence=report.confidence,
                    horizontal_accuracy=report.horizontal_accuracy,
                )
                locations.append((base_location, location_info))
            accessory_location_map[accessory.master_key] = locations
        return accessory_location_map

    async def setup(self) -> None:
        self.update_task = asyncio.create_task(
            self._update_timer(), name="FruityTag Location updater"
        )

    async def shutdown(self) -> None:
        await self.account.close()
        if self.update_task:
            self.update_task.cancel()

    async def get_accessory_info(
        self, accessory: Accessory
    ) -> FruityTagStaticAccessoryInfo | FruityTagRollingAccessoryInfo | None:
        if accessory.provider != AccessoryProvider.FRUITYTAG:
            LOG.error(f"Accessory {accessory.id} is not provided by {type(self)}")
            return None
        if accessory.type == AccessoryType.FRUITYTAG_STATIC:
            statement = select(FruityTagStaticAccessoryInfo).where(
                FruityTagStaticAccessoryInfo.id == accessory.id
            )

        elif accessory.type == AccessoryType.FRUITYTAG_ROLLING:
            statement = select(FruityTagRollingAccessoryInfo).where(
                FruityTagRollingAccessoryInfo.id == accessory.id
            )
        else:
            LOG.error(f"Unknown accessory type {accessory.type}")
            return None

        with self.db.session as session:
            result = session.exec(statement)
            res = result.one_or_none()
            return res

    async def get_location_info(
        self, accessory: Accessory, location: Location
    ) -> FruityTagLocationInfo | None:
        statement = select(FruityTagLocationInfo).where(
            FruityTagLocationInfo.id == location.id
        )
        with self.db.session as session:
            result = session.exec(statement=statement)
            return result.one_or_none()

    async def add_location_info(
        self, location_info: FruityTagLocationInfo
    ) -> FruityTagLocationInfo:
        with self.db.session as session:
            session.add(location_info)
            session.commit()
            session.refresh(location_info)
        return location_info

    async def create_accessory(
        self, user: User, accessory: Accessory, options: AccessoryOptions
    ) -> FruityTagStaticAccessoryInfo | FruityTagRollingAccessoryInfo:
        if options.type == AccessoryType.FRUITYTAG_STATIC:
            if len(options.master_key) != 28:  # pyright:ignore[reportAttributeAccessIssue]
                raise RuntimeError("Master key must be 28 bytes long")
            info = FruityTagStaticAccessoryInfo(
                id=accessory.id,
                master_key=options.master_key,  # pyright:ignore[reportAttributeAccessIssue]
            )
        elif options.type == AccessoryType.FRUITYTAG_ROLLING:
            if len(options.master_key) != 28:  # pyright:ignore[reportAttributeAccessIssue]
                raise RuntimeError("Master key must be 28 bytes long")
            elif len(options.series_key) != 32:  # pyright:ignore[reportAttributeAccessIssue]
                raise RuntimeError("Series key must be 32 bytes long")
            elif len(options.secondary_key) != 32:  # pyright:ignore[reportAttributeAccessIssue]
                raise RuntimeError("Secondary key must be 32 bytes long")

            info = FruityTagRollingAccessoryInfo(
                id=accessory.id,
                master_key=options.master_key,  # pyright:ignore[reportAttributeAccessIssue]
                series_key=options.series_key,  # pyright:ignore[reportAttributeAccessIssue]
                secondary_key=options.secondary_key,  # pyright:ignore[reportAttributeAccessIssue]
                paired_at=options.paired_at.astimezone(datetime.UTC),  # pyright:ignore[reportAttributeAccessIssue]
                alignment_date=(
                    options.alignment_date.astimezone(datetime.UTC)  # pyright:ignore[reportAttributeAccessIssue]
                    if options.alignment_date  # pyright:ignore[reportAttributeAccessIssue]
                    else None
                ),  # pyright:ignore[reportAttributeAccessIssue]
                alignment_index=options.alignment_index,  # pyright:ignore[reportAttributeAccessIssue]
            )
        else:
            raise UNKNOW_PROVIDER_EXCEPTION

        with self.db.session as session:
            session.add(info)
            session.commit()
            session.refresh(info)

        return info

    async def update_accessory_info(
        self, accessory: Accessory, options: AccessoryOptions
    ) -> FruityTagStaticAccessoryInfo | FruityTagRollingAccessoryInfo:
        info = await self.get_accessory_info(accessory)
        if not info:
            raise UNKNOW_PROVIDER_EXCEPTION
        if accessory.type == AccessoryType.FRUITYTAG_STATIC:
            info.master_key = (
                options.master_key  # pyright:ignore[reportAttributeAccessIssue]
            )
        elif accessory.type == AccessoryType.FRUITYTAG_ROLLING:
            info.master_key = (
                options.master_key  # pyright:ignore[reportAttributeAccessIssue]
            )
            info.series_key = (
                options.series_key  # pyright:ignore[reportAttributeAccessIssue]
            )
            info.secondary_key = (
                options.secondary_key  # pyright:ignore[reportAttributeAccessIssue]
            )
            info.paired_at = options.paired_at.astimezone(  # pyright:ignore[reportAttributeAccessIssue]
                datetime.UTC
            )
            info.alignment_date = (
                options.alignment_date.astimezone(datetime.UTC)  # pyright:ignore[reportAttributeAccessIssue]
                if (
                    options.alignment_date  # pyright:ignore[reportAttributeAccessIssue]
                    and (options.alignment_index or info.alignment.index)  # pyright:ignore[reportAttributeAccessIssue]
                )
                else None
            )

            info.alignment_index = (
                options.alignment_index if info.alignment_date else None  # pyright:ignore[reportAttributeAccessIssue]
            )
        else:
            raise UNKNOW_PROVIDER_EXCEPTION

        with self.db.session as session:
            session.add(info)
            session.commit()
            session.refresh(info)

        return info
