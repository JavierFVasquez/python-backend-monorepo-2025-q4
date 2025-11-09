import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from libs.common.errors import BaseAPIError
from libs.common.jsonapi import serialize_error
from libs.common.logging import request_id_ctx

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and propagate request IDs for distributed tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Set request_id in context for structured logging
        token = request_id_ctx.set(request_id)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Reset context
            request_id_ctx.reset(token)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle errors and return JSON:API compliant error responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except BaseAPIError as e:
            logger.error(
                f"API Error: {e.detail}",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "status_code": e.status,
                    "title": e.title,
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            return JSONResponse(
                status_code=int(e.status),
                content=serialize_error(e.status, e.title, e.detail, e.source),
            )
        except Exception as e:
            logger.exception(
                "Unhandled exception",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "path": request.url.path,
                    "method": request.method,
                    "error_type": type(e).__name__,
                },
            )
            return JSONResponse(
                status_code=500,
                content=serialize_error(
                    "500", "Internal Server Error", "An unexpected error occurred"
                ),
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with timing and status."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Log incoming request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "event": "request_started",
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "request_id": request_id,
            },
        )

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log completed request
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code}",
                extra={
                    "event": "request_completed",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "request_id": request_id,
                },
            )
            return response
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} - Error",
                extra={
                    "event": "request_failed",
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(e).__name__,
                    "request_id": request_id,
                },
            )
            raise

