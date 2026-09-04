from pydantic import BaseModel


class VehicleInfoRequest(BaseModel):
    license_plate: str


class Vehicle(BaseModel):
    license_plate: str
    manufacturer: str
    model: str
    year: int
    color: str


class VehicleInfoResponse(BaseModel):
    success: bool = True
    vehicle: Vehicle
    summary: str


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
