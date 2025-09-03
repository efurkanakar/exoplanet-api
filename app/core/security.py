"""
API key based authentication dependency.

This is a very simple header-based security mechanism.
In production, prefer OAuth2 or JWT for stronger security.
"""

from fastapi import Header, HTTPException, status
from app.core.config import settings


def api_key_auth(x_api_key: str = Header(default="")):
    """
    Dependency that enforces API key authentication.

    Args:
        x_api_key (str): Value from `X-API-Key` request header.

    Raises:
        HTTPException: 401 Unauthorized if the key is invalid.
    """
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )