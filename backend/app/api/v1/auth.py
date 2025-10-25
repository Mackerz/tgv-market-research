"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

from app.core.database import get_db
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_token,
    GOOGLE_CLIENT_ID,
)
from app.core.constants import (
    LOGIN_RATE_LIMIT,
    GOOGLE_LOGIN_RATE_LIMIT,
    COOKIE_MAX_AGE_SECONDS,
)
from app.schemas.user import LoginRequest, LoginResponse, GoogleLoginRequest, User as UserSchema
from app.models.user import User
from app.crud.user import user as user_crud

router = APIRouter(prefix="/api/auth", tags=["authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=LoginResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(
    request: Request,
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login with username and password.
    Returns access token and sets it as an HTTP-only cookie.
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=os.getenv("ENVIRONMENT") == "production",  # Only HTTPS in production
        samesite="lax",
        max_age=COOKIE_MAX_AGE_SECONDS,
    )

    return LoginResponse(
        access_token=access_token,
        user=UserSchema.model_validate(user)
    )


@router.post("/google", response_model=LoginResponse)
@limiter.limit(GOOGLE_LOGIN_RATE_LIMIT)
async def google_login(
    request: Request,
    google_data: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login with Google OAuth.
    Verifies the Google credential token and creates/updates user.
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication not configured",
        )

    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            google_data.credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Get user info from Google token
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name", email.split("@")[0])

        # Check if user exists
        user = user_crud.get_by_google_id(db, google_id)
        if not user:
            # Check if email already exists
            user = user_crud.get_by_email(db, email)
            if user:
                # Link Google account to existing user
                user.google_id = google_id
                db.commit()
                db.refresh(user)
            else:
                # Create new user
                username = email.split("@")[0]
                # Ensure unique username
                counter = 1
                original_username = username
                while user_crud.get_by_username(db, username):
                    username = f"{original_username}{counter}"
                    counter += 1

                user = user_crud.create_google_user(
                    db,
                    email=email,
                    username=username,
                    full_name=name,
                    google_id=google_id
                )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Create access token
        access_token = create_access_token(data={"sub": user.id})

        # Set HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=os.getenv("ENVIRONMENT") == "production",
            samesite="lax",
            max_age=COOKIE_MAX_AGE_SECONDS,
        )

        return LoginResponse(
            access_token=access_token,
            user=UserSchema.model_validate(user)
        )

    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
        )


@router.post("/logout")
async def logout(response: Response):
    """
    Logout by clearing the access token cookie.
    """
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Get the currently authenticated user.
    Returns 401 if not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return current_user


@router.get("/check")
async def check_auth(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Check if user is authenticated.
    Returns status without requiring authentication.
    """
    environment = os.getenv("ENVIRONMENT", "development")
    return {
        "authenticated": current_user is not None,
        "environment": environment,
        "google_sso_enabled": GOOGLE_CLIENT_ID is not None,
    }
