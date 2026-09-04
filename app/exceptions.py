class VehicleLookupError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 200) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


class InvalidPlateError(VehicleLookupError):
    def __init__(self) -> None:
        super().__init__("INVALID_PLATE", "License plate must be 7 or 8 digits.")


class VehicleNotFoundError(VehicleLookupError):
    def __init__(self, plate: str) -> None:
        super().__init__(
            "VEHICLE_NOT_FOUND", f"No vehicle found for license plate {plate}."
        )


class UpstreamTimeoutError(VehicleLookupError):
    def __init__(self) -> None:
        super().__init__(
            "UPSTREAM_TIMEOUT",
            "The vehicle registry did not respond in time.",
            status_code=504,
        )


class UpstreamUnavailableError(VehicleLookupError):
    def __init__(self) -> None:
        super().__init__(
            "UPSTREAM_UNAVAILABLE",
            "The vehicle registry is unavailable.",
            status_code=502,
        )


class UpstreamResponseError(VehicleLookupError):
    def __init__(self) -> None:
        super().__init__(
            "UPSTREAM_ERROR",
            "The vehicle registry returned an unexpected response.",
            status_code=502,
        )
