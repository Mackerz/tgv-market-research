"""Main router that aggregates all API v1 routers"""
from fastapi import APIRouter

from app.api.v1 import auth, users, surveys, submissions, media, reporting, settings, health

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router)  # Health checks first for easy monitoring
api_router.include_router(auth.router)  # Authentication endpoints
api_router.include_router(users.router)
api_router.include_router(surveys.router)
api_router.include_router(submissions.router)
api_router.include_router(media.router)
api_router.include_router(reporting.router)
api_router.include_router(settings.router)
