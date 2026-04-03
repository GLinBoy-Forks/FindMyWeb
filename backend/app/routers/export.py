import asyncio
import uuid
from datetime import timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from gpx import GPX, Track, TrackSegment, Waypoint
from gpx.types import Latitude, Longitude

from app.database import db
from app.database.models import Accessory, Location, User
from app.dependencies import get_current_active_user
from app.helpers import ACCESSORY_NOT_FOUND_EXCEPTION
from app.models.export import ExportRequest

export = APIRouter()


def get_description(location: Location) -> str | None:
    cmt = str()
    cmt += f"Battery: {location.battery_level.value if location.battery_level else 'Unknown'}\n"
    return cmt


def generate_gpx(accessory: Accessory, locations: list[Location]) -> str:
    points = [
        Waypoint(
            lat=Latitude(location.lat),
            lon=Longitude(location.lon),
            time=(
                location.timestamp.astimezone(timezone.utc)
                if location.timestamp
                else None
            ),
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
    return gpx.to_string(pretty_print=False)


@export.post(
    "/gpx/{accessory_id}",
    response_model=str,
    responses={
        200: {
            "content": {
                "application/gpx+xml": {"schema": {"type": "string"}},
            },
        }
    },
)
async def export_gpx(
    current_user: Annotated[User, Depends(get_current_active_user)],
    accessory_id: uuid.UUID,
    export_req: ExportRequest,
) -> Response:
    if accessory := await db.get_accessory_by_id(
        user=current_user, accessory_id=accessory_id
    ):
        try:
            async with asyncio.timeout(30):
                locations = await db.get_locations(
                    accessory=accessory,
                    start_date=export_req.start,
                    end_date=export_req.end,
                )
                gpx = await asyncio.to_thread(generate_gpx, accessory, locations)
        except TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range too long to process",
            )

        return Response(
            content=gpx,
            media_type="application/gpx+xml",
            headers={
                "Content-Disposition": f'attachment; filename="{accessory.name}.gpx"'
            },
        )

    raise ACCESSORY_NOT_FOUND_EXCEPTION
