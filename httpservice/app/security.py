import os

import fastapi
import starlette
from fastapi.security.api_key import APIKeyHeader


ALLOWED_API_KEY = os.environ["ALLOWED_API_KEY"]
API_KEY_NAME = "X-API-KEY"
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def check_apikey_header(
    api_key_header: str = fastapi.Security(api_key_header_auth),
):
    """Enforce API-key security

    Assert that the provided X-API-KEY header value matches the ALLOWED_API_KEY
    read from environment
    """
    if api_key_header != ALLOWED_API_KEY:
        raise fastapi.HTTPException(
            status_code=starlette.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
