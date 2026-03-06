from enum import Enum

from pydantic import BaseModel


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class CookieType(Enum):
    REFRESH = "refresh_token"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class JWTToken(BaseModel):
    exp: int
    type: TokenType


class AccessTokenData(JWTToken):
    userid: str
    is_admin: bool
    username: str


class RefreshTokenData(JWTToken):
    userid: str
