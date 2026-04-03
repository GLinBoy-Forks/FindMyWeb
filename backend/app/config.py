import logging.config
import tomllib
from typing import Optional

from pydantic import BaseModel, Field
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
    allow_credentials: bool = False
    cors_origins: list[str] = Field(default_factory=list)
    cors_headers: list[str] = Field(default_factory=list)
    cors_methods: list[str] = Field(default_factory=list)
    expose_headers: list[str] = Field(default_factory=list)


class CompressionConfig(BaseModel):
    enabled: bool = True
    minimum_size: int = 1000


class FrontendConfig(BaseModel):
    path: str


class Config(BaseModel):
    jwt: JWTConfig
    admin: AdminConfig
    findmy: FindMyConfig
    db: DBConfig
    frontend: FrontendConfig
    compression: CompressionConfig = CompressionConfig()
    log: LoggingSettings | None = None
    cors: Optional[CorsConfig] | None = None


def load_config(path: str = "config.toml") -> Config:
    fd = open(path, "rb")
    cfg_dict = tomllib.load(fd)
    fd.close()

    cfg = Config.model_validate(cfg_dict)
    if cfg.log:
        logging.config.dictConfig(cfg.log.model_dump())

    return cfg
