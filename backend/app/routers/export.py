from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.database import db
from app.database.models import Accessory, User
from app.dependencies import get_current_active_user
from app.helpers import ACCESSORY_NOT_FOUND_EXCEPTION, LOCATION_NOT_FOUND_EXCEPTION
from app.models.export import (
    ExportRequest
)
from app.database.models import Location
from app.providers import fruitytag

from gpx import GPX, Metadata, Track, TrackSegment, Waypoint
from gpx.types import Latitude, Longitude
from datetime import timezone, datetime
import asyncio

export = APIRouter()

def get_description(location: Location) -> str | None:
    cmt = str()
    cmt += f"Battery: {location.battery_level.value if location.battery_level else 'Unknown'}\n"
    cmt += f"Accuracy: {location.horizontal_accuracy if location.horizontal_accuracy else 'Unknown'}\n"
    cmt += f"Status: {format(location.status, '02x') if location.status else 'Unknown'}"
    return cmt

def generate_gpx(accessory: Accessory, locations: list[Location]) -> str:
    points = [
        Waypoint(
            lat=Latitude(location.lat),
            lon=Longitude(location.lon),
            time=location.timestamp.astimezone(timezone.utc) if location.timestamp else None,
            cmt=get_description(location),
        )
        for location in locations
    ]

    segment = TrackSegment(trkpt=points)
    track = Track(name=accessory.name, trkseg=[segment])

    gpx = GPX(
        creator="FindMyWeb",
        trk=[track],
    )
    return gpx.to_string()

@export.post("/gpx")
async def export_gpx(
    current_user: Annotated[User, Depends(get_current_active_user)],
    export_req: ExportRequest,
) -> Response:
    if accessory := await db.get_accessory(user=current_user, name=export_req.name):
        try:
            async with asyncio.timeout(30):
                locations = await fruitytag.get_locations(
                    accessory=accessory,
                    start_date=export_req.start,
                    end_date=export_req.end,
                )
                gpx = await asyncio.to_thread(generate_gpx, accessory, locations)
        except TimeoutError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Date range too long to process")

        return Response(content=gpx, media_type="application/gpx+xml", headers={"Content-Disposition": f"attachment; filename=\"{accessory.name}.gpx\""})

    raise ACCESSORY_NOT_FOUND_EXCEPTION
