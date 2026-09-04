from fastapi import APIRouter

from app.controllers.vehicle_controller import get_vehicle_info
from app.schemas.vehicle import ErrorResponse, VehicleInfoRequest, VehicleInfoResponse

router = APIRouter(tags=["vehicle"])


@router.post(
    "/vehicle-info",
    response_model=VehicleInfoResponse,
    responses={502: {"model": ErrorResponse}, 504: {"model": ErrorResponse}},
    summary="Look up a vehicle by license plate",
    description="Fetch vehicle details from the registry for a license plate.",
)
async def vehicle_info(payload: VehicleInfoRequest) -> VehicleInfoResponse:
    """Look up vehicle details by license plate."""
    return await get_vehicle_info(payload)


@router.get("/health", summary="Health check")
async def health() -> dict[str, str]:
    """Basic health check"""
    return {"status": "ok"}