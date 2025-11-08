import os

from fastapi import Header, HTTPException

from libs.common.jsonapi import serialize_error


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail=serialize_error("500", "Configuration Error", "API_KEY not configured"),
        )

    if x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail=serialize_error("401", "Unauthorized", "Invalid API key"),
        )

    return x_api_key

