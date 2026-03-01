from typing import Optional

import tomllib
from pydantic import BaseModel
from pydantic_settings_logging import LoggingSettings


class JWTConfig(BaseModel):
    secret: str
    secret_refresh: str
    algorithm: str
    expire: int  # in minutes
    expire_refresh: int  # in hours


class AdminConfig(BaseModel):
    name: str
    password: str


class FindMyConfig(BaseModel):
    libs_path: str
    account: str


class DBConfig(BaseModel):
    uri: str


class CorsConfig(BaseModel):
    allow_credentials: bool
    cors_origins: list[str]
    cors_headers: list[str]
    cors_methods: list[str]


class FrontendConfig(BaseModel):
    path: str


class Config(BaseModel):
    jwt: JWTConfig
    admin: AdminConfig
    findmy: FindMyConfig
    db: DBConfig
    frontend: FrontendConfig
    log: LoggingSettings | None = None
    cors: Optional[CorsConfig] | None = None


def load_config(path: str = "config.toml") -> Config:
    fd = open(path, "rb")
    cfg_dict = tomllib.load(fd)
    fd.close()

    cfg = Config.model_validate(cfg_dict)

    return cfg
