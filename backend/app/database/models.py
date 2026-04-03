import datetime
import uuid
from enum import IntFlag

from pydantic import Base64Bytes
from pydantic_extra_types.coordinate import Latitude, Longitude
from sqlmodel import Column, Field, LargeBinary, Relationship, SQLModel

from app.providers.types import (
    AccessoryProvider,
    AccessoryType,
    BatteryLevel,
    LocationType,
)


class Permissions(IntFlag):
    """
    Permission for a user.
        USER = 0
        ADMIN = 1
    """

    USER = 0b0
    ADMIN = 0b1


class Location(SQLModel, table=True):
    """Base class for locations."""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        unique=True,
        description="Unique identfier for this location",
    )
    lat: Latitude = Field(description="Latitude of this location")
    lon: Longitude = Field(description="Longitude of this location")
    battery_level: BatteryLevel = Field(
        default=BatteryLevel.UNKNOWN,
        description="Battery level at the time of this location",
    )
    timestamp: datetime.datetime = Field(
        description="Time the accessory was seen at this location (UTC)"
    )

    type: LocationType = Field(
        default=LocationType.BASIC, description="Type of the location"
    )
    accessory_id: uuid.UUID = Field(
        foreign_key="accessory.id",
        index=True,
        description="The id of the accessory associated with this location",
    )
    accessory: "Accessory" = Relationship(
        back_populates="locations", cascade_delete=False
    )


class LocationInfo(SQLModel, table=False):
    """Additional info provided by a location."""

    id: uuid.UUID = Field(
        foreign_key="location.id",
        index=True,
        primary_key=True,
        description="Unique identifier of the location associated with this info",
    )


class FruityTagLocationInfo(LocationInfo, table=True):
    """Additional data provided by a FruityTag location."""

    status: int | None = Field(
        description="The status byte advertised by the FruityTag (see: https://codeberg.org/Misom/FindMyWeb/src/branch/main/firmware/src/tag/tag.h#L13)"
    )
    confidence: int | None = Field(
        description="Confidence of this location as a value between 1 and 3"
    )
    horizontal_accuracy: int | None = Field(
        description="Horizontal accuracy of the location (presumably in meters)"
    )


class Accessory(SQLModel, table=True):
    """Base class for accessories."""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier of this accessory",
    )

    user: "User" = Relationship(back_populates="accessories", cascade_delete=False)
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
        description="Unique identifier of the user associated with this accessory",
    )

    type: AccessoryType = Field(description="Type of the accessory")
    provider: AccessoryProvider = Field(
        unique=False, description="Provider of the accessory"
    )

    name: str = Field(unique=False, max_length=32, description="Name of the accessory")
    color: str = Field(
        unique=False,
        min_length=3,
        max_length=8,
        description="Color of the accessory in hex",
    )
    icon: str = Field(
        unique=False,
        max_length=32,
        description="Icon of the accessory (see iconify: https://icon-sets.iconify.design)",
    )

    locations: list[Location] = Relationship(
        back_populates="accessory", cascade_delete=True
    )


class AccessoryInfo(SQLModel, table=False):
    """Class holding additional info for accessories."""

    id: uuid.UUID = Field(
        foreign_key="accessory.id",
        index=True,
        primary_key=True,
        description="Unique identifier for the accessory associated with this info",
    )


class FruityTagStaticAccessoryInfo(AccessoryInfo, table=True):
    """Class for storing FruityTags with a static key."""

    master_key: Base64Bytes = Field(
        sa_column=Column(LargeBinary),
        min_length=28,
        max_length=28,
        description="Master key (private key) of the FruityTag",
    )


class FruityTagRollingAccessoryInfo(AccessoryInfo, table=True):
    """Class for storing FruityTags with a rolling key."""

    master_key: Base64Bytes = Field(
        sa_column=Column(LargeBinary),
        min_length=28,
        max_length=28,
        description="Master key (private key) of the FruityTag",
    )
    series_key: Base64Bytes = Field(
        sa_column=Column(LargeBinary),
        min_length=32,
        max_length=32,
        description="Series key (skn) of the FruityTag",
    )
    secondary_key: Base64Bytes = Field(
        sa_column=Column(LargeBinary),
        min_length=32,
        max_length=32,
        description="Secondary key (sks) of the FruityTag",
    )
    paired_at: datetime.datetime = Field(
        unique=False,
        description="Date when this accessory was first paired (time it was setup) (UTC)",
    )

    alignment_date: datetime.datetime | None = Field(
        unique=False,
        default=None,
        description="Date this accessory was realigned (got the current time) (UTC)",
    )
    alignment_index: int | None = Field(
        unique=False, default=None, description="Last known series key index"
    )


class User(SQLModel, table=True):
    """Class for storing the users."""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier of this user",
    )
    username: str = Field(
        unique=True, max_length=32, description="Username of this user"
    )
    password_hash: str = Field(
        unique=False,
        min_length=64,
        max_length=64,
        description="Hash of the user's password",
    )
    permissions: int = Field(
        default=Permissions.USER, description="Permssions of the user"
    )
    accessories: list[Accessory] = Relationship(
        back_populates="user", cascade_delete=True
    )
