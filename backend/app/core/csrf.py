"""
CSRF Protection

Implements CSRF token generation and validation for state-changing operations.
"""

from fastapi import Header, HTTPException, status
from secrets import token_urlsafe
import time
from typing import Optional
import os


class CSRFProtection:
    """CSRF token generation and validation"""

    def __init__(self, secret_key: Optional[str] = None, max_age: int = 3600):
        """
        Initialize CSRF protection.

        Args:
            secret_key: Secret key for token generation (from environment)
            max_age: Maximum age of CSRF tokens in seconds (default: 1 hour)
        """
        self.secret_key = secret_key or os.getenv("SECRET_KEY", "change-me-in-production")
        self.max_age = max_age

    def generate_token(self, session_id: Optional[str] = None) -> str:
        """
        Generate a CSRF token.

        Args:
            session_id: Optional session identifier

        Returns:
            CSRF token string
        """
        timestamp = str(int(time.time()))
        random_token = token_urlsafe(32)

        # Format: random_token.timestamp
        return f"{random_token}.{timestamp}"

    def verify_token(self, token: str) -> bool:
        """
        Verify a CSRF token is valid and not expired.

        Args:
            token: CSRF token to verify

        Returns:
            True if valid and not expired, False otherwise
        """
        if not token:
            return False

        try:
            # Parse token
            parts = token.split('.')
            if len(parts) != 2:
                return False

            token_value, timestamp = parts

            # Check token format (should be base64 URL-safe)
            if len(token_value) != 43:  # URL-safe base64 of 32 bytes
                return False

            # Check if expired
            token_time = int(timestamp)
            current_time = int(time.time())
            if current_time - token_time > self.max_age:
                return False

            return True

        except (ValueError, AttributeError):
            return False


# Global instance
csrf_protection = CSRFProtection()


async def verify_csrf_token(
    x_csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token")
) -> str:
    """
    FastAPI dependency to verify CSRF token.

    Args:
        x_csrf_token: CSRF token from X-CSRF-Token header

    Returns:
        The CSRF token if valid

    Raises:
        HTTPException: If CSRF token is missing or invalid
    """
    # Check if CSRF protection is enabled
    if not os.getenv("CSRF_PROTECTION_ENABLED", "false").lower() == "true":
        # CSRF protection disabled (for development or API-only mode)
        return "csrf-disabled"

    if not x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required. Include X-CSRF-Token header.",
            headers={"X-CSRF-Required": "true"},
        )

    if not csrf_protection.verify_token(x_csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired CSRF token",
        )

    return x_csrf_token


def generate_csrf_token() -> str:
    """Helper function to generate CSRF token"""
    return csrf_protection.generate_token()
