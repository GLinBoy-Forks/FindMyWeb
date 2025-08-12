class WrongColorFormat(Exception):
    """Raised when the color for an `Accessory` doesn't use the HTML color format"""


class NotBase64(Exception):
    """Raised when a string is not base64 decodable"""
