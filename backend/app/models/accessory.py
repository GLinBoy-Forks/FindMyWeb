from app.database.models import Accessory
from pydantic import BaseModel


class CreateAccessoryRequest(BaseModel):
    name: str
    color: str
    icon: str
    private_key: str | None = None


class AccessoryBaseRequest(BaseModel):
    name: str


class AccessoryRequest(AccessoryBaseRequest):
    pass


class AdvertisementRequest(AccessoryBaseRequest):
    pass


class AdvertisementResponse(BaseModel):
    advertisement_key: str


class RemoveAccessoryRequest(AccessoryBaseRequest):
    pass


class AccessoriesResponse(BaseModel):
    accessories: list[Accessory]


class AccessoryResponse(BaseModel):
    accessory: Accessory


class PrivateKeyResponse(BaseModel):
    private_key: str
