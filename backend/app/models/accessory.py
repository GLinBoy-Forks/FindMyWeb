from typing import Literal, Union

from app.database.models import (
    Accessory,
    AccessoryInfo,
    FruityTagRollingAccessoryInfo,
    FruityTagStaticAccessoryInfo,
)
from app.providers.types import AccessoryType
from pydantic import AwareDatetime, Base64Bytes, BaseModel, Field
from pydantic_extra_types import Color


class AccessoryOptions(BaseModel):
    type: Literal[AccessoryType.FRUITYTAG_STATIC, AccessoryType.FRUITYTAG_ROLLING]


class FruityTagStaticAccessoryOptions(AccessoryOptions):
    type: Literal[AccessoryType.FRUITYTAG_STATIC]  # pyright: ignore[reportIncompatibleVariableOverride]
    master_key: Base64Bytes


class FruityTagRollingAccessoryOptions(AccessoryOptions):
    type: Literal[AccessoryType.FRUITYTAG_ROLLING]  # pyright: ignore[reportIncompatibleVariableOverride]
    master_key: Base64Bytes
    series_key: Base64Bytes
    secondary_key: Base64Bytes

    paired_at: AwareDatetime

    alignment_date: AwareDatetime | None = None
    alignment_index: int | None = None


class BaseAccessoryOptions(BaseModel):
    name: str
    color: Color
    icon: str


class CreateAccessoryRequest(BaseAccessoryOptions):
    options: Union[
        FruityTagStaticAccessoryOptions, FruityTagRollingAccessoryOptions
    ] = Field(discriminator="type")


class UpdateAccessoryRequest(BaseAccessoryOptions):
    options: Union[
        FruityTagStaticAccessoryOptions, FruityTagRollingAccessoryOptions
    ] = Field(discriminator="type")


class AccessoryBaseRequest(BaseModel):
    pass


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
    info: Union[
        FruityTagRollingAccessoryInfo, FruityTagStaticAccessoryInfo, AccessoryInfo, None
    ]
