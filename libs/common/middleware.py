import logging
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from libs.common.errors import BaseAPIError
from libs.common.jsonapi import serialize_error

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except BaseAPIError as e:
            logger.error(
                f"API Error: {e.detail}",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "status": e.status,
                    "title": e.title,
                },
            )
            return JSONResponse(
                status_code=int(e.status),
                content=serialize_error(e.status, e.title, e.detail, e.source),
            )
        except Exception as e:
            logger.exception(
                "Unhandled exception",
                extra={"request_id": getattr(request.state, "request_id", "unknown")},
            )
            return JSONResponse(
                status_code=500,
                content=serialize_error(
                    "500", "Internal Server Error", "An unexpected error occurred"
                ),
            )

