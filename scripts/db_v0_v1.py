import argparse
import asyncio
import base64
import datetime
import os
import sys
import uuid

from sqlalchemy import create_engine, text
from sqlmodel import SQLModel, select

sys.path.append(
    os.path.realpath(os.path.join(os.path.realpath(sys.argv[0]), "..", "..", "backend"))
)
from app.database import db
from app.providers import FruityTag
from app.providers.types import (AccessoryProvider, AccessoryType,
                                 BatteryLevel, LocationType)
from app.database.models import Accessory, FruityTagStaticAccessoryInfo, FruityTagLocationInfo, Location

async def migrate_accessories(session):
    all_accessories = session.execute(text("SELECT * FROM old_accessory")).all()
    for private_key, name, color, icon, user_id in all_accessories:
        new_accessory = Accessory(user_id=uuid.UUID(user_id), type=AccessoryType.FRUITYTAG_STATIC, provider=AccessoryProvider.FRUITYTAG, name=name, color=color, icon=icon)
        session.add(new_accessory)
        accessory_info = FruityTagStaticAccessoryInfo(id=new_accessory.id, master_key=base64.b64decode(private_key))
        session.add(accessory_info)
    session.execute(text("DROP TABLE old_accessory"))

async def migrate_locations(provider, session):
    all_locations = session.execute(text("SELECT * FROM old_location")).all()

    LEVELMAP = {
        "BATTERY_FULL": BatteryLevel.FULL,
        "BATTERY_MEDIUM": BatteryLevel.MEDIUM,
        "BATTERY_LOW": BatteryLevel.LOW,
        "BATTERY_CRITICAL": BatteryLevel.CRITICAL,
    }

    for (
        old_id,
        lat,
        lon,
        timestamp,
        accessory_key,
        battery_level,
        status,
        confidence,
        horizontal_accuracy,
    ) in all_locations:
        parent_accessory = session.exec(select(FruityTagStaticAccessoryInfo).where(FruityTagStaticAccessoryInfo.master_key==base64.b64decode(accessory_key))).one()
        dt_time = datetime.datetime.fromisoformat(timestamp + "Z")
        new_id = await provider._hash_report(
            base64.b64decode(accessory_key),
            lat,
            lon,
            dt_time,
        )

        new_location = Location(id=new_id, lat=float(lat), lon=float(lon), battery_level=LEVELMAP.get(
            battery_level, BatteryLevel.UNKNOWN
        ), timestamp=dt_time, type=LocationType.FRUITYTAG, accessory_id=parent_accessory.id)

        session.add(new_location)

        new_location_info = FruityTagLocationInfo(
            id=new_id,
            status=int(status) if status else None,
            confidence=int(confidence) if confidence else None,
            horizontal_accuracy=int(horizontal_accuracy) if horizontal_accuracy else None
        )
        session.add(new_location_info)
    session.execute(text("DROP TABLE old_location"))


async def main():
    parser = argparse.ArgumentParser(
        "A script to migrate the pre prelease db to the v1 schema."
    )
    args = parser.parse_args()
    provider = FruityTag(db)
    with db.session as session:
        session.execute(text("DROP INDEX ix_accessory_user_id"))
        session.execute(text("DROP INDEX ix_location_accessory_key"))

        session.execute(text("ALTER TABLE user RENAME COLUMN admin to permissions"))
        session.execute(text("ALTER TABLE accessory RENAME TO old_accessory"))
        session.execute(text("ALTER TABLE location RENAME TO old_location"))

        session.commit()

    SQLModel.metadata.create_all(db.engine)
    with db.session as session:
        await migrate_accessories(session)
        await migrate_locations(provider, session)
        session.commit()
asyncio.run(main())
