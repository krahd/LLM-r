from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from llmr.config import settings


def require_api_key(authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> None:
    """Dependency to require API key when `settings.require_auth` is true.

    Accepts either `Authorization: Bearer <key>` or `X-API-Key: <key>`.
    """
    if not settings.require_auth:
        return None

    expected = settings.api_key
    if not expected:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Server API key not configured")

    provided = None
    if authorization:
        auth = authorization.strip()
        if auth.lower().startswith("bearer "):
            provided = auth[7:].strip()
        else:
            provided = auth

    if x_api_key and not provided:
        provided = x_api_key.strip()

    if provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return None
