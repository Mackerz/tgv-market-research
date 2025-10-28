"""
Authentication and Authorization

Implements two authentication methods:
1. API key-based authentication for admin endpoints and programmatic access
2. Session-based authentication with username/password and Google SSO for web users

Survey response endpoints remain public for easy user access.
"""

import os
import secrets
from datetime import datetime, timedelta

import bcrypt
from fastapi import Cookie, Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User

# API Key header name
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        raise RuntimeError("🔴 CRITICAL: SECRET_KEY must be set in production environment!")
    # Only allow fallback in development
    SECRET_KEY = secrets.token_hex(32)
    import logging
    logging.warning("⚠️ Using randomly generated SECRET_KEY (dev mode only - sessions will reset on restart)")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Get API key from environment (or Secret Manager in production)
def get_api_key_from_config() -> str | None:
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
    import logging

    expected_api_key = get_api_key_from_config()
    environment = os.getenv("ENVIRONMENT", "development")

    # Only allow bypass in explicit development mode
    if not expected_api_key:
        if environment == "production":
            # NEVER bypass in production - fail closed
            logging.error("🔴 CRITICAL: API key not configured in production!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication not configured (critical configuration error)",
            )
        # Allow bypass only in development
        logging.warning("⚠️ No API key configured - authentication disabled (dev mode only!)")
        return "dev-mode-bypass"

    # Check if API key was provided
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide via X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(api_key, expected_api_key):
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


# ============================================================================
# Password Authentication Functions
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password for storage using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    # Ensure sub (subject) is a string as per JWT spec
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticate a user by username and password with account lockout."""
    from datetime import datetime, timedelta

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.now(user.locked_until.tzinfo):
        return None  # Account is locked

    # Reset lockout if time has passed
    if user.locked_until and user.locked_until <= datetime.now(user.locked_until.tzinfo):
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    if not user.hashed_password:
        return None  # Google SSO user without password

    if not verify_password(password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(user.created_at.tzinfo) + timedelta(minutes=15)
            db.commit()
            return None

        db.commit()
        return None

    # Reset failed attempts on successful login
    if user.failed_login_attempts and user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    return user


async def get_current_user_from_token(
    token: str | None = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> User | None:
    """Get the current user from JWT token in cookie."""
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        # Convert string back to int
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError):
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user


def _validate_api_key_internal(api_key: str) -> User | None:
    """
    Internal function to validate API key and return a fake admin user if valid.

    Returns:
        User object if API key is valid, None otherwise
    """
    expected_api_key = get_api_key_from_config()
    environment = os.getenv("ENVIRONMENT", "development")

    # Allow dev mode bypass if explicitly configured
    if not expected_api_key and environment != "production":
        # Dev mode - create a fake admin user
        return User(
            id=0,
            username="dev-mode",
            email="dev@example.com",
            is_admin=True,
            is_active=True
        )

    # Validate API key
    if expected_api_key and secrets.compare_digest(api_key, expected_api_key):
        # Valid API key - create a fake admin user
        return User(
            id=0,
            username="api-key",
            email="api@example.com",
            is_admin=True,
            is_active=True
        )

    return None


async def get_current_user(
    request: Request,
    api_key: str | None = Security(api_key_header),
    token_user: User | None = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Get the current user from either API key or session token.

    Returns None if not authenticated (for optional auth).
    For required auth, use require_auth or require_admin.
    """
    # Check API key first (for backward compatibility)
    if api_key:
        api_user = _validate_api_key_internal(api_key)
        if api_user:
            return api_user

    # Check session token
    if token_user:
        return token_user

    return None


async def require_auth(
    current_user: User | None = Depends(get_current_user),
    api_key: str | None = Security(api_key_header)
) -> User:
    """
    Require authentication via session token or API key.
    Raises 401 if not authenticated.
    """
    # Allow API key authentication
    if api_key:
        api_user = _validate_api_key_internal(api_key)
        if api_user:
            return api_user

    # Require session authentication
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return current_user


async def require_admin(
    current_user: User = Depends(require_auth)
) -> User:
    """
    Require admin privileges.
    Raises 403 if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return current_user
