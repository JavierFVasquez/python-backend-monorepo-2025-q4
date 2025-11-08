import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = httpx.Timeout(timeout=timeout, connect=5.0)
        self.max_retries = max_retries

    async def _request(
        self,
        method: str,
        path: str,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        headers["X-API-Key"] = self.api_key
        if request_id:
            headers["X-Request-ID"] = request_id

        url = f"{self.base_url}{path}"
        retry_count = 0

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while retry_count <= self.max_retries:
                try:
                    response = await client.request(method, url, headers=headers, **kwargs)

                    if response.status_code < 500:
                        return response

                    if retry_count == self.max_retries:
                        return response

                    wait_time = 2**retry_count
                    logger.warning(
                        f"Request failed with {response.status_code}, "
                        f"retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    retry_count += 1

                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    if retry_count == self.max_retries:
                        raise

                    wait_time = 2**retry_count
                    logger.warning(
                        f"Request failed with {type(e).__name__}, "
                        f"retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    retry_count += 1

        raise httpx.RequestError("Max retries exceeded")

    async def get(self, path: str, request_id: str | None = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", path, request_id, **kwargs)

    async def post(self, path: str, request_id: str | None = None, **kwargs: Any) -> httpx.Response:
        return await self._request("POST", path, request_id, **kwargs)

    async def patch(
        self, path: str, request_id: str | None = None, **kwargs: Any
    ) -> httpx.Response:
        return await self._request("PATCH", path, request_id, **kwargs)

    async def delete(
        self, path: str, request_id: str | None = None, **kwargs: Any
    ) -> httpx.Response:
        return await self._request("DELETE", path, request_id, **kwargs)

