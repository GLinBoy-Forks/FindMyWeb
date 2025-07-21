import datetime
import uuid
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, max_length=32)
    password_hash: str
    admin: bool = Field(default=False)
    accessories: Optional[list["Accessory"]] = Relationship(
        back_populates="user", cascade_delete=True
    )


class Accessory(SQLModel, table=True):
    private_key: str = Field(unique=True, max_length=144, primary_key=True)
    name: str = Field(unique=True, max_length=32)
    color: str = Field(unique=False, max_length=7)
    icon: str = Field(unique=False, max_length=32)

    locations: list["Location"] = Relationship(
        back_populates="accessory", cascade_delete=True
    )

    user_id: uuid.UUID = Field(default=None, foreign_key="user.id", index=True)

    user: User = Relationship(back_populates="accessories")


class Location(SQLModel, table=True):
    id: str = Field(primary_key=True, unique=True, max_length=64)
    lat: float
    lon: float
    timestamp: datetime.datetime
    accessory_key: str = Field(
        default=None, foreign_key="accessory.private_key", index=True
    )
    accessory: Accessory = Relationship(back_populates="locations")
