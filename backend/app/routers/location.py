import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.database import db
from app.database.models import Location, User
from app.dependencies import get_current_active_user
from app.helpers import ACCESSORY_NOT_FOUND_EXCEPTION, LOCATION_NOT_FOUND_EXCEPTION
from app.models.location import LocationResponse, LocationsRequest, LocationsResponse

location = APIRouter()


@location.get("/{accessory_id}")
async def get_location(
    current_user: Annotated[User, Depends(get_current_active_user)],
    accessory_id: uuid.UUID,
) -> Location:
    if accessory := await db.get_accessory_by_id(
        user=current_user, accessory_id=accessory_id
    ):
        location = await db.get_last_location(accessory=accessory)
        if location:
            return location
        else:
            raise LOCATION_NOT_FOUND_EXCEPTION
    raise ACCESSORY_NOT_FOUND_EXCEPTION


@location.get("/info/{accessory_id}/{location_id}")
async def get_location_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
    accessory_id: uuid.UUID,
    location_id: uuid.UUID,
) -> LocationResponse:
    if accessory := await db.get_accessory_by_id(
        user=current_user, accessory_id=accessory_id
    ):
        location = await db.get_location_by_id(
            accessory=accessory, location_id=location_id
        )
        if location:
            info = await db.get_location_info(accessory=accessory, location=location)
            return LocationResponse(location=location, info=info)  # pyright: ignore[reportArgumentType]
        else:
            raise LOCATION_NOT_FOUND_EXCEPTION
    raise ACCESSORY_NOT_FOUND_EXCEPTION


@location.post("/duration/{accessory_id}")
async def get_locations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    accessory_id: uuid.UUID,
    locations_req: LocationsRequest,
) -> LocationsResponse:
    if accessory := await db.get_accessory_by_id(
        user=current_user, accessory_id=accessory_id
    ):
        return LocationsResponse(
            locations=await db.get_locations(
                accessory=accessory,
                start_date=locations_req.start,
                end_date=locations_req.end,
            )
        )

    raise ACCESSORY_NOT_FOUND_EXCEPTION
