import datetime

from database.models import Accessory, Location
from pydantic import BaseModel


class CreateAccessoryRequest(BaseModel):
    name: str
    color: str
    icon: str
    private_key: str | None = None


class UpdateUserRequest(BaseModel):
    name: str
    password: str
    is_admin: bool


class CreateUserRequest(BaseModel):
    name: str
    password: str
    is_admin: bool


class RemoveUserRequest(BaseModel):
    name: str


class AccessoryBaseRequest(BaseModel):
    name: str


class LocationsRequest(AccessoryBaseRequest):
    start: datetime.datetime
    end: datetime.datetime


class LocationRequest(AccessoryBaseRequest):
    location_id: str | None = None


class AccessoryRequest(AccessoryBaseRequest):
    pass


class AdvertisementRequest(AccessoryBaseRequest):
    pass


class RemoveAccessoryRequest(AccessoryBaseRequest):
    pass


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class AdvertisementResponse(BaseModel):
    advertisement_key: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class AccessoriesResponse(BaseModel):
    accessories: list[Accessory]


class AccessoryResponse(BaseModel):
    accessory: Accessory


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


class PrivateKeyResponse(BaseModel):
    private_key: str


class UserInfo(BaseModel):
    name: str
    superuser: bool
    is_admin: bool


class UsersResponse(BaseModel):
    users: list[UserInfo]
