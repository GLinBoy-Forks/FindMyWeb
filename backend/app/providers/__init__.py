from app.const import MAINTENANCE_MODE
from app.database import db

from .types import AccessoryProvider, AccessoryType

ACCESSORY_TYPE_TO_PROVIDER = {
    AccessoryType.FRUITYTAG_ROLLING: AccessoryProvider.FRUITYTAG,
    AccessoryType.FRUITYTAG_STATIC: AccessoryProvider.FRUITYTAG,
}

if not MAINTENANCE_MODE:
    from .fruitytag import FruityTag

    available_providers = {AccessoryProvider.FRUITYTAG: FruityTag(db=db)}
else:
    available_providers = dict()
