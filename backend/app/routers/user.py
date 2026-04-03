import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.const import CONFIG
from app.database import db
from app.database.exceptions import UserDoesNotExist, UserExists
from app.database.models import Permissions, User
from app.dependencies import ensure_permissions, get_current_active_user
from app.helpers import USER_NOT_FOUND_EXCEPTION
from app.models.common import OKStatusResponse, StatusResponse
from app.models.user import (
    ChangePasswordRequest,
    CreateUserRequest,
    UpdateUserRequest,
    UserInfo,
    UsersResponse,
)

user = APIRouter()


@user.get("/list")
async def get_users(
    current_user: Annotated[User, Depends(ensure_permissions(Permissions.ADMIN))],
) -> UsersResponse:
    all_users = await db.get_users()

    return UsersResponse(
        users=[
            UserInfo(
                id=user.id,
                name=user.username,
                permissions=user.permissions,
                superuser=CONFIG.admin.name == user.username,
            )
            for user in all_users
        ]
    )


@user.post("/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    change_password_req: ChangePasswordRequest,
) -> StatusResponse:
    if not await db.verify(current_user, change_password_req.old_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Old password is incorrect"
        )

    await db.update_password(current_user, change_password_req.new_password)
    return OKStatusResponse()


@user.post("/create", status_code=status.HTTP_200_OK)
async def create_user(
    current_user: Annotated[User, Depends(ensure_permissions(Permissions.ADMIN))],
    create_user_req: CreateUserRequest,
) -> StatusResponse:
    try:
        await db.add_user(
            username=create_user_req.name,
            password=create_user_req.password,
            permissions=create_user_req.permissions,
        )
    except UserExists as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
    return OKStatusResponse()


@user.delete("/{id}", status_code=status.HTTP_200_OK)
async def remove_user(
    current_user: Annotated[User, Depends(ensure_permissions(Permissions.ADMIN))],
    id: uuid.UUID,
) -> StatusResponse:
    if id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can't remove yourself"
        )
    try:
        await db.remove_user(id=id)
    except UserDoesNotExist as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
    return OKStatusResponse()


@user.post("/{id}", status_code=status.HTTP_200_OK)
async def update_user(
    current_user: Annotated[User, Depends(ensure_permissions(Permissions.ADMIN))],
    id: uuid.UUID,
    update_user_req: UpdateUserRequest,
) -> StatusResponse:
    if id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can't update yourself"
        )

    user = await db.get_user_by_id(id)
    if not user:
        raise USER_NOT_FOUND_EXCEPTION

    if update_user_req.password:
        user = await db.update_password(user, update_user_req.password)
    if (
        update_user_req.permissions is not None
        and user.permissions != update_user_req.permissions
    ):
        user.permissions = update_user_req.permissions
    if update_user_req.name and user.username != update_user_req.name:
        user.username = update_user_req.name

    await db.update_user(user)
    return OKStatusResponse()
