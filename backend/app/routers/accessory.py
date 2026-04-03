import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import db
from app.database.exceptions import AccessoryDoesntExist, ProviderDoesntExist
from app.database.models import Accessory, User
from app.dependencies import get_current_active_user
from app.helpers import ACCESSORY_NOT_FOUND_EXCEPTION, UNKNOW_PROVIDER_EXCEPTION
from app.models.accessory import (
    AccessoriesResponse,
    AccessoryResponse,
    CreateAccessoryRequest,
    UpdateAccessoryRequest,
)
from app.models.common import OKStatusResponse, StatusResponse
from app.providers import ACCESSORY_TYPE_TO_PROVIDER

accessory = APIRouter()


@accessory.get("")
async def get_accessories(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccessoriesResponse:
    accessories = await db.get_accessories_by_user(current_user)

    return AccessoriesResponse(accessories=accessories)


@accessory.get("/{id}")
async def get_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)], id: uuid.UUID
) -> AccessoryResponse:
    try:
        accessory = await db.get_accessory_by_id(user=current_user, accessory_id=id)
    except AccessoryDoesntExist:
        raise ACCESSORY_NOT_FOUND_EXCEPTION

    info = await db.get_accessory_info(accessory)
    return AccessoryResponse(accessory=accessory, info=info)


@accessory.delete("/{id}", status_code=status.HTTP_200_OK)
async def remove_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)], id: uuid.UUID
) -> StatusResponse:
    try:
        accessory = await db.get_accessory_by_id(user=current_user, accessory_id=id)
    except AccessoryDoesntExist:
        raise ACCESSORY_NOT_FOUND_EXCEPTION

    await db.remove_accessory(accessory=accessory)
    return OKStatusResponse()


@accessory.post("/{id}")
async def update_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    id: uuid.UUID,
    update_accessory_req: UpdateAccessoryRequest,
) -> Accessory:
    try:
        accessory = await db.get_accessory_by_id(user=current_user, accessory_id=id)
    except AccessoryDoesntExist:
        raise ACCESSORY_NOT_FOUND_EXCEPTION

    accessory.name = update_accessory_req.name
    accessory.color = update_accessory_req.color.as_hex()
    accessory.icon = update_accessory_req.icon

    accessory = await db.update_accessory(accessory)

    await db.update_accessory_info(accessory, update_accessory_req.options)

    return accessory


@accessory.post("")
async def create_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    create_accessory_req: CreateAccessoryRequest,
) -> AccessoryResponse:
    try:
        provider = await db.get_provider(
            ACCESSORY_TYPE_TO_PROVIDER[create_accessory_req.options.type]
        )
    except ProviderDoesntExist:
        raise UNKNOW_PROVIDER_EXCEPTION
    base_accessory = Accessory(
        user_id=current_user.id,
        type=create_accessory_req.options.type,
        provider=ACCESSORY_TYPE_TO_PROVIDER[create_accessory_req.options.type],
        name=create_accessory_req.name,
        color=create_accessory_req.color.as_hex(),
        icon=create_accessory_req.icon,
    )
    base_accessory = await db.add_accessory(base_accessory)

    try:
        info = await provider.create_accessory(
            current_user, accessory=base_accessory, options=create_accessory_req.options
        )
    except Exception as ex:
        await db.remove_accessory(base_accessory)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
    return AccessoryResponse(accessory=base_accessory, info=info)
