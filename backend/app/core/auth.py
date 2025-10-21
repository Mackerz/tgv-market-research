"""
Authentication and Authorization

Implements API key-based authentication for admin endpoints.
Survey response endpoints remain public for easy user access.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
import secrets
from typing import Optional

# API Key header name
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API key from environment (or Secret Manager in production)
def get_api_key_from_config() -> Optional[str]:
    """
    Get API key from environment configuration.

    In production, this should be stored in GCP Secret Manager.
    For development, set API_KEY environment variable.

    Returns:
        API key string or None if not configured
    """
    api_key = os.getenv("API_KEY")

    if not api_key:
        # Try to get from GCP Secret Manager
        try:
            from app.integrations.gcp.secrets import get_secret
            api_key = get_secret("api-key")
        except:
            pass

    return api_key


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Use this during setup to generate keys for clients.
    Store the generated key in GCP Secret Manager.

    Returns:
        32-character hexadecimal API key
    """
    return secrets.token_hex(32)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key for admin endpoints.

    Args:
        api_key: API key from request header

    Returns:
        The API key if valid

    Raises:
        HTTPException: If API key is missing or invalid
    """
    expected_api_key = get_api_key_from_config()

    # If no API key is configured, allow all requests (development mode)
    if not expected_api_key:
        import logging
        logging.warning("⚠️ No API key configured - authentication disabled (dev mode only!)")
        return "dev-mode-bypass"

    # Check if API key was provided
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide via X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Verify API key matches
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key


# Dependency for protecting admin endpoints
RequireAPIKey = Security(verify_api_key)


def is_auth_enabled() -> bool:
    """Check if authentication is enabled."""
    return get_api_key_from_config() is not None
