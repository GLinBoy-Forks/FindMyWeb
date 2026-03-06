from typing import Annotated

from fastapi import APIRouter, Depends

from app.database import db
from app.database.models import User
from app.dependencies import get_current_active_user
from app.helpers import ACCESSORY_NOT_FOUND_EXCEPTION, LOCATION_NOT_FOUND_EXCEPTION
from app.models.location import (
    BasicLocation,
    LocationRequest,
    LocationResponse,
    LocationsRequest,
    LocationsResponse,
)
from app.providers import fruitytag

location = APIRouter()


@location.post("")
async def get_location(
    current_user: Annotated[User, Depends(get_current_active_user)],
    locations_req: LocationRequest,
):
    if accessory := await db.get_accessory(user=current_user, name=locations_req.name):
        if not locations_req.location_id:
            return LocationResponse(
                location=await db.get_last_location(accessory=accessory)
            )
        else:
            location = LocationResponse(
                location=await db.get_location(
                    accessory=accessory, location_id=locations_req.location_id
                )
            )
            if not location:
                raise LOCATION_NOT_FOUND_EXCEPTION
            return location
    raise ACCESSORY_NOT_FOUND_EXCEPTION


@location.post("/duration")
async def get_locations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    locations_req: LocationsRequest,
):
    if accessory := await db.get_accessory(user=current_user, name=locations_req.name):
        return LocationsResponse(
            locations=[
                BasicLocation.from_location(location)
                for location in await fruitytag.get_locations(
                    accessory=accessory,
                    start_date=locations_req.start,
                    end_date=locations_req.end,
                )
            ]
        )

    raise ACCESSORY_NOT_FOUND_EXCEPTION
