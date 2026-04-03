from typing import Union

from app.database.models import FruityTagLocationInfo, Location, LocationInfo
from pydantic import AwareDatetime, BaseModel

from .accessory import AccessoryBaseRequest


class LocationsResponse(BaseModel):
    locations: list[Location]


class LocationResponse(BaseModel):
    location: Location
    info: Union[FruityTagLocationInfo, None] = None


class LocationsRequest(AccessoryBaseRequest):
    start: AwareDatetime
    end: AwareDatetime
