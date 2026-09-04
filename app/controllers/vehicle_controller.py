from app.schemas.vehicle import Vehicle, VehicleInfoRequest, VehicleInfoResponse
from app.services.vehicle_service import look_up_vehicle


def build_summary(vehicle: Vehicle) -> str:
    return (
        f"{vehicle.manufacturer} {vehicle.model} {vehicle.year}, "
        f"{vehicle.color} ({vehicle.license_plate})"
    )


async def get_vehicle_info(payload: VehicleInfoRequest) -> VehicleInfoResponse:
    vehicle = await look_up_vehicle(payload.license_plate)
    return VehicleInfoResponse(vehicle=vehicle, summary=build_summary(vehicle))
