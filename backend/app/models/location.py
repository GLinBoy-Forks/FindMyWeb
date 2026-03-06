import datetime

from app.database.models import Location
from pydantic import BaseModel

from .accessory import AccessoryBaseRequest


class BasicLocation(BaseModel):
    id: str
    lat: float
    lon: float
    timestamp: datetime.datetime

    @staticmethod
    def from_location(location: Location):
        return BasicLocation(
            id=location.id,
            lat=location.lat,
            lon=location.lon,
            timestamp=location.timestamp,
        )


class LocationsResponse(BaseModel):
    locations: list[BasicLocation]


class LocationResponse(BaseModel):
    location: Location | None


class LocationsRequest(AccessoryBaseRequest):
    start: datetime.datetime
    end: datetime.datetime


class LocationRequest(AccessoryBaseRequest):
    location_id: str | None = None
