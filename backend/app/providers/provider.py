import datetime
from typing import Any

from app.database import Database
from app.database.models import (Accessory, AccessoryInfo, Location,
                                 LocationInfo, User)
from app.models.accessory import AccessoryOptions


class Provider:
    def __init__(self, db: Database):
        pass

    async def setup(self) -> None:
        """Called during application bringup"""
        raise NotImplementedError("Provider must implement setup")

    async def shutdown(self) -> None:
        """Called during application shutdown"""
        raise NotImplementedError("Provider must implement shutdown")

    async def get_accessory_info(self, accessory: Accessory) -> Any | None:
        """Should return additional infos for the provided accessory"""
        raise NotImplementedError("Provider must implement get_accessory_info")

    async def get_locations(
        self,
        accessory: Accessory,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        limit: int | None = None,
    ) -> list[Location]:
        """Should return all locations associated with the accessory"""
        raise NotImplementedError("Provider must implement get_locations")

    async def get_last_location(self, accessory: Accessory) -> Location | None:
        """Should return the last known location of the accessory"""
        raise NotImplementedError("Provider must implement get_last_location")

    async def get_location_info(
        self, accessory: Accessory, location: Location
    ) -> LocationInfo | None:
        """Should return the location info associated with the location"""
        raise NotImplementedError("Provider must implement get_location_info")

    async def get_accessories(self, user: User) -> list[Accessory]:
        """Should return all accessories owned by the user"""
        raise NotImplementedError("Provider must implement get_accessories")

    async def create_accessory(
        self, user: User, accessory: Accessory, options: AccessoryOptions
    ) -> AccessoryInfo:
        """Should create the accessory infos return them"""
        raise NotImplementedError("Provider must implement create_accessory")

    async def update_accessory_info(
        self, accessory: Accessory, options: AccessoryOptions
    ) -> AccessoryInfo:
        """Should update the accessroy infos and return them"""
        raise NotImplementedError("Provider must implement update_accessory_info")

    async def remove_accessory(self, accessory: Accessory) -> None:
        """Should remove the accessory"""
        raise NotImplementedError("Provider must implement remove_accessory")

    async def accessory_exists(self, accessory: Accessory) -> bool:
        """Should check if the accessory exists"""
        raise NotImplementedError("Provider must implement accessory_exists")
