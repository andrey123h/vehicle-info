import os
import re

import httpx

from app.exceptions import (
    InvalidPlateError,
    UpstreamResponseError,
    UpstreamTimeoutError,
    UpstreamUnavailableError,
    VehicleNotFoundError,
)
from app.schemas.vehicle import Vehicle

VEHICLE_SERVICE_URL = os.getenv(
    "VEHICLE_SERVICE_URL",
    "https://insurance-webhook-945894769129.us-central1.run.app/vehicle-info",
)
UPSTREAM_TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "10"))

# Regex pattern to match valid license plates (7 or 8 digits)
PLATE_PATTERN = re.compile(r"^\d{7,8}$") 
# Regex pattern to match separators (spaces, hyphens, or periods)
SEPARATORS = re.compile(r"[\s\-.]")


def normalize_plate(raw: str | None) -> str:
    return SEPARATORS.sub("", raw or "")


async def look_up_vehicle(raw_plate: str) -> Vehicle:
    """Fetch vehicle details from the registry for a license plate.

    The plate is normalized and validated before the call.

    Raises:
        InvalidPlateError: Plate is not 7 or 8 digits.
        VehicleNotFoundError: Registry has no vehicle for the plate.
        UpstreamTimeoutError: Registry did not respond within the timeout.
        UpstreamUnavailableError: Registry could not be reached.
        UpstreamResponseError: Registry replied with an unexpected status or body.
    """
    plate = normalize_plate(raw_plate)
    if not PLATE_PATTERN.match(plate):
        raise InvalidPlateError()

    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
            response = await client.post(
                VEHICLE_SERVICE_URL, json={"license_plate": plate}
            )
    except httpx.TimeoutException as exc:
        raise UpstreamTimeoutError() from exc
    except httpx.HTTPError as exc:
        raise UpstreamUnavailableError() from exc

    if response.status_code == 404:
        raise VehicleNotFoundError(plate)
    if response.status_code in (400, 422):
        raise InvalidPlateError()
    if response.status_code != 200:
        raise UpstreamResponseError()

    try:
        return Vehicle.model_validate(response.json()["data"])
    except Exception as exc:
        raise UpstreamResponseError() from exc
