import logging
import uuid
from typing import Annotated, Callable

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.const import CONFIG
from app.database import db
from app.database.models import Permissions, User
from app.helpers import CREDENTIALS_EXCEPTION, USER_NOT_PERMITTED_EXCEPTION
from app.models.login import AccessTokenData, TokenType

LOG = logging.getLogger(__name__)


async def get_current_user(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/api/login"))],
):
    try:
        payload = jwt.decode(
            jwt=token, key=CONFIG.jwt.secret, algorithms=[CONFIG.jwt.algorithm]
        )
        access_token = AccessTokenData.model_validate(payload)
        if access_token.type != TokenType.ACCESS or access_token.userid is None:
            raise CREDENTIALS_EXCEPTION

        userid = uuid.UUID(access_token.userid)

    except (InvalidTokenError, TypeError) as ex:
        LOG.debug(f"Error occured during login attempt: {ex}")
        raise CREDENTIALS_EXCEPTION

    user = await db.get_user_by_id(userid)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


def ensure_permissions(permission: Permissions) -> Callable:
    async def check_user_permissions(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        if (int(current_user.permissions) & permission) != permission:
            raise USER_NOT_PERMITTED_EXCEPTION
        return current_user

    return check_user_permissions
