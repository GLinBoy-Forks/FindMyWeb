import uuid
from typing import Literal

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    id: uuid.UUID
    name: str
    superuser: bool
    permissions: int


class UsersResponse(BaseModel):
    users: list[UserInfo]


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateUserRequest(BaseModel):
    name: str | None = Field(min_length=1)
    password: str | None = Field(min_length=1)
    permissions: int | None


class CreateUserRequest(BaseModel):
    name: str
    password: str
    permissions: int


class LogoutResponse(BaseModel):
    detail: Literal["success"]


class RemoveUserRequest(BaseModel):
    name: str
