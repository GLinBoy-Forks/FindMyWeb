from datetime import datetime, timedelta, timezone
from enum import Enum

import jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from jwt.exceptions import InvalidTokenError

from const import CONFIG

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class CookieType(Enum):
    REFRESH = "refresh_token"


def create_refresh_token(
    data: dict, expires_delta: timedelta = timedelta(hours=CONFIG.jwt.expire_refresh)
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    to_encode.update({"type": TokenType.REFRESH.value})

    encoded_jwt = jwt.encode(
        payload=to_encode, key=CONFIG.jwt.secret_refresh, algorithm=CONFIG.jwt.algorithm
    )
    return encoded_jwt


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(minutes=CONFIG.jwt.expire)
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    to_encode.update({"type": TokenType.ACCESS.value})

    encoded_jwt = jwt.encode(
        payload=to_encode, key=CONFIG.jwt.secret, algorithm=CONFIG.jwt.algorithm
    )
    return encoded_jwt
