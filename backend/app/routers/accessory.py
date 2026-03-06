from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import db
from app.database.exceptions import AccessoryExists
from app.database.models import Accessory, User
from app.dependencies import get_current_active_user
from app.helpers import ACCESSORY_NOT_FOUND_EXCEPTION
from app.models.accessory import (
    AccessoriesResponse,
    AccessoryRequest,
    AccessoryResponse,
    AdvertisementRequest,
    AdvertisementResponse,
    CreateAccessoryRequest,
    PrivateKeyResponse,
    RemoveAccessoryRequest,
)
from app.providers import fruitytag
from app.providers.fruitytag.exceptions import NotBase64, WrongColorFormat

accessory = APIRouter()


@accessory.post("")
async def get_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    accesory_req: AccessoryRequest,
) -> AccessoryResponse:
    if accessory := await db.get_accessory(user=current_user, name=accesory_req.name):
        return AccessoryResponse(accessory=accessory)

    raise ACCESSORY_NOT_FOUND_EXCEPTION


@accessory.get("")
async def get_accessories(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccessoriesResponse:
    accessories = await db.get_accessories_by_user(current_user)

    return AccessoriesResponse(accessories=accessories)


@accessory.post("/create")
async def create_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    create_accessory_req: CreateAccessoryRequest,
) -> Accessory:
    try:
        new_accessory = await fruitytag.create_accessory(
            user=current_user,
            name=create_accessory_req.name,
            color=create_accessory_req.color,
            icon=create_accessory_req.icon,
            private_key_b64=create_accessory_req.private_key,
        )

    except (WrongColorFormat, NotBase64, AccessoryExists) as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )

    return new_accessory


@accessory.post("/update")
async def update_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    update_accessory_req: CreateAccessoryRequest,
) -> Accessory:
    try:
        new_accessory = await fruitytag.update_accessory(
            user=current_user,
            name=update_accessory_req.name,
            color=update_accessory_req.color,
            icon=update_accessory_req.icon,
            private_key_b64=update_accessory_req.private_key,
        )

    except (WrongColorFormat, NotBase64, AccessoryExists) as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )

    return new_accessory


@accessory.post("/remove", status_code=status.HTTP_200_OK)
async def remove_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    remove_accessory_req: RemoveAccessoryRequest,
):
    if not await fruitytag.remove_accessory(
        user=current_user, name=remove_accessory_req.name
    ):
        raise ACCESSORY_NOT_FOUND_EXCEPTION


@accessory.post("/advertisement")
async def get_advertise_key(
    current_user: Annotated[User, Depends(get_current_active_user)],
    advertisement_req: AdvertisementRequest,
) -> AdvertisementResponse:
    key_pair = await fruitytag.get_key_pair_by_name(
        current_user, advertisement_req.name
    )
    if not key_pair:
        raise ACCESSORY_NOT_FOUND_EXCEPTION

    return AdvertisementResponse(advertisement_key=key_pair.adv_key_b64)


@accessory.get("/privatekey")
async def create_private_key(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PrivateKeyResponse:
    new_priv_key = await fruitytag.gen_private_key()

    return PrivateKeyResponse(private_key=new_priv_key.private_key_b64)
