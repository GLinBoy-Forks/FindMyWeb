import datetime
import uuid
from enum import IntEnum

from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class BatteryLevel(IntEnum):
    BATTERY_FULL = 0b00
    BATTERY_MEDIUM = 0b01
    BATTERY_LOW = 0b10
    BATTERY_CRITICAL = 0b11

    @staticmethod
    def from_status(status: int):
        return BatteryLevel(status >> 6)


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

    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    user: User = Relationship(back_populates="accessories")


class Location(SQLModel, table=True):
    id: str = Field(primary_key=True, unique=True, max_length=64)
    lat: float
    lon: float
    timestamp: datetime.datetime | None
    battery_level: BatteryLevel | None
    status: int | None
    confidence: int | None
    horizontal_accuracy: int | None
    accessory_key: str = Field(foreign_key="accessory.private_key", index=True)
    accessory: Accessory = Relationship(back_populates="locations")
