from typing import Literal

from pydantic import BaseModel


class UserInfo(BaseModel):
    name: str
    superuser: bool
    is_admin: bool


class UsersResponse(BaseModel):
    users: list[UserInfo]


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateUserRequest(BaseModel):
    name: str
    password: str
    is_admin: bool


class CreateUserRequest(BaseModel):
    name: str
    password: str
    is_admin: bool


class LogoutResponse(BaseModel):
    detail: Literal["success"]


class RemoveUserRequest(BaseModel):
    name: str
