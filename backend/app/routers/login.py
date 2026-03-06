import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from app.const import CONFIG
from app.database import db
from app.database.models import User
from app.dependencies import get_current_active_user
from app.helpers import (
    CREDENTIALS_EXCEPTION,
    USER_NOT_PERMITTED_EXCEPTION,
)
from app.models.login import (
    AccessTokenData,
    CookieType,
    LoginResponse,
    RefreshTokenData,
    TokenType,
)

login = APIRouter()


def create_refresh_token(
    userid: str,
    expires_delta: timedelta = timedelta(hours=CONFIG.jwt.expire_refresh),
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta

    token_data = RefreshTokenData(
        userid=userid,
        exp=int(expire.timestamp()),
        type=TokenType.REFRESH,
    )

    encoded_jwt = jwt.encode(
        payload=token_data.model_dump(mode="json"),
        key=CONFIG.jwt.secret_refresh,
        algorithm=CONFIG.jwt.algorithm,
    )
    return encoded_jwt


def create_access_token(
    userid: str,
    is_admin: bool,
    username: str,
    expires_delta: timedelta = timedelta(minutes=CONFIG.jwt.expire),
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta

    token_data = AccessTokenData(
        userid=userid,
        is_admin=is_admin,
        username=username,
        exp=int(expire.timestamp()),
        type=TokenType.ACCESS,
    )

    encoded_jwt = jwt.encode(
        payload=token_data.model_dump(mode="json"),
        key=CONFIG.jwt.secret,
        algorithm=CONFIG.jwt.algorithm,
    )
    return encoded_jwt


@login.post("")
async def login_user(
    response: Response, login_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> LoginResponse:
    user = await db.get_user(login_data.username)
    if not user or not await db.verify(user, login_data.password):
        raise USER_NOT_PERMITTED_EXCEPTION

    access_token = create_access_token(
        userid=str(user.id), is_admin=user.admin, username=user.username
    )

    refresh_token = create_refresh_token(userid=str(user.id))

    response.set_cookie(
        key=CookieType.REFRESH.value,
        value=refresh_token,
    )

    return LoginResponse(access_token=access_token, token_type="bearer")


@login.delete("")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Response:
    response = Response(status_code=status.HTTP_200_OK)
    response.delete_cookie(
        key=CookieType.REFRESH.value,
    )
    return response


@login.get("/refresh")
async def refresh(request: Request):
    refresh_token = request.cookies.get(CookieType.REFRESH.value, None)

    if not refresh_token:
        raise CREDENTIALS_EXCEPTION

    try:
        payload = jwt.decode(
            jwt=refresh_token,
            key=CONFIG.jwt.secret_refresh,
            algorithms=[CONFIG.jwt.algorithm],
        )

        token_data = RefreshTokenData.model_validate(payload)

        if token_data.type != TokenType.REFRESH or token_data.userid is None:
            raise CREDENTIALS_EXCEPTION

        userid = uuid.UUID(token_data.userid)

    except (InvalidTokenError, TypeError):
        raise CREDENTIALS_EXCEPTION

    user = await db.get_user_by_id(userid)

    if not user:
        raise CREDENTIALS_EXCEPTION

    access_token = create_access_token(
        userid=str(user.id), is_admin=user.admin, username=user.username
    )
    return LoginResponse(access_token=access_token, token_type="bearer")
