from enum import Enum


class BatteryLevel(str, Enum):
    FULL = "Full"
    MEDIUM = "Medium"
    LOW = "Low"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


class LocationType(str, Enum):
    BASIC = "Basic"
    FRUITYTAG = "FruityTag"


class AccessoryProvider(str, Enum):
    FRUITYTAG = "FruityTag"


class AccessoryType(str, Enum):
    FRUITYTAG_STATIC = "FruityTagStatic"
    FRUITYTAG_ROLLING = "FruityTagRolling"
