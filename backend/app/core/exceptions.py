class DigitalTwinException(Exception):
    """Base exception class for Digital Twin Application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SensorDataValidationError(DigitalTwinException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class DigitalTwinDivergenceError(DigitalTwinException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)


class RepositoryError(DigitalTwinException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=503)


class ModelInferenceError(DigitalTwinException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=500)
