from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import VehicleLookupError
from app.routers import vehicle
from app.schemas.vehicle import ErrorResponse

app = FastAPI(title="Vehicle Info API", version="1.0.0")

app.include_router(vehicle.router)


def error_response(error_code: str, message: str, status_code: int) -> JSONResponse:
    body = ErrorResponse(error_code=error_code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


@app.exception_handler(VehicleLookupError)
async def handle_lookup_error(request: Request, exc: VehicleLookupError) -> JSONResponse:
    return error_response(exc.error_code, exc.message, exc.status_code)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        "INVALID_REQUEST",
        'Expected a JSON body: {"license_plate": "12345678"}',
        status_code=200,
    )
