class AccessoryExists(Exception):
    """Raised when the accessory's name or private_key already exist"""


class AccessoryDoesntExist(Exception):
    """Raised when the accessory doesn't exist"""


class UserExists(Exception):
    """Raised when the user already exists"""


class UserDoesNotExist(Exception):
    """Raised when the user does not exist"""


class LocationExists(Exception):
    """Raised when the location already exists"""
