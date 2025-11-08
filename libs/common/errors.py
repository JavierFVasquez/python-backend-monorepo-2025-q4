from typing import Any


class BaseAPIError(Exception):
    def __init__(
        self, status: str, title: str, detail: str, source: dict[str, Any] | None = None
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.source = source or {}
        super().__init__(detail)


class NotFoundError(BaseAPIError):
    def __init__(self, detail: str, source: dict[str, Any] | None = None) -> None:
        super().__init__(status="404", title="Not Found", detail=detail, source=source)


class ValidationError(BaseAPIError):
    def __init__(self, detail: str, source: dict[str, Any] | None = None) -> None:
        super().__init__(
            status="422", title="Validation Error", detail=detail, source=source
        )


class UnauthorizedError(BaseAPIError):
    def __init__(self, detail: str = "Unauthorized", source: dict[str, Any] | None = None) -> None:
        super().__init__(status="401", title="Unauthorized", detail=detail, source=source)


class InternalServerError(BaseAPIError):
    def __init__(
        self, detail: str = "Internal Server Error", source: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            status="500", title="Internal Server Error", detail=detail, source=source
        )

