from libs.common.errors import (
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    InternalServerError,
)


def test_not_found_error() -> None:
    error = NotFoundError("Resource not found")

    assert error.status == "404"
    assert error.title == "Not Found"
    assert error.detail == "Resource not found"


def test_validation_error() -> None:
    error = ValidationError("Invalid input")

    assert error.status == "422"
    assert error.title == "Validation Error"
    assert error.detail == "Invalid input"


def test_unauthorized_error() -> None:
    error = UnauthorizedError()

    assert error.status == "401"
    assert error.title == "Unauthorized"
    assert error.detail == "Unauthorized"


def test_internal_server_error() -> None:
    error = InternalServerError()

    assert error.status == "500"
    assert error.title == "Internal Server Error"
    assert error.detail == "Internal Server Error"

