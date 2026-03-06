from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.const import CONFIG
from app.database import db
from app.database.exceptions import UserExists
from app.database.models import User
from app.dependencies import ensure_is_admin, get_current_active_user
from app.helpers import USER_NOT_FOUND_EXCEPTION
from app.models.user import (
    ChangePasswordRequest,
    CreateUserRequest,
    RemoveUserRequest,
    UpdateUserRequest,
    UserInfo,
    UsersResponse,
)

user = APIRouter()


@user.get("/list")
async def get_users(current_user: Annotated[User, Depends(ensure_is_admin)]):
    all_users = await db.get_users()

    return UsersResponse(
        users=[
            UserInfo(
                name=user.username,
                is_admin=user.admin,
                superuser=CONFIG.admin.name == user.username,
            )
            for user in all_users
        ]
    )


@user.post("/create", status_code=status.HTTP_200_OK)
async def create_user(
    current_user: Annotated[User, Depends(ensure_is_admin)],
    create_user_req: CreateUserRequest,
):
    try:
        await db.add_user(
            username=create_user_req.name,
            password=create_user_req.password,
            is_admin=create_user_req.is_admin,
        )
    except UserExists as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@user.post("/remove", status_code=status.HTTP_200_OK)
async def remove_user(
    current_user: Annotated[User, Depends(ensure_is_admin)],
    remove_user_req: RemoveUserRequest,
):
    if current_user.username == remove_user_req.name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can't remove yourself"
        )

    try:
        await db.remove_user(username=remove_user_req.name)
    except UserExists as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@user.post("/update", status_code=status.HTTP_200_OK)
async def update_user(
    current_user: Annotated[User, Depends(ensure_is_admin)],
    update_user_req: UpdateUserRequest,
):
    if current_user.username == update_user_req.name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can't update yourself"
        )

    user = await db.get_user(update_user_req.name)
    if not user:
        raise USER_NOT_FOUND_EXCEPTION

    user = await db.update_password(user, update_user_req.password)
    if user.admin != update_user_req.is_admin:
        user.admin = update_user_req.is_admin
        await db.update_user(user)


@user.post("/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    change_password_req: ChangePasswordRequest,
):
    if not await db.verify(current_user, change_password_req.old_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Old password is incorrect"
        )

    await db.update_password(current_user, change_password_req.new_password)
