"""FastAPI application entry point"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import logging

from app.core.database import get_db, engine, Base
from app.api.v1 import api_router

# Import models to ensure they're registered with SQLAlchemy
from app.models.user import User, Post
from app.models.survey import Survey, Submission, Response
from app.models.media import Media
from app.models.settings import ReportSettings, QuestionDisplayName

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Market Research Backend API",
    version="1.0.0",
    description="Backend API for Market Research Survey Platform"
)

# Log startup information
logger.info("🚀 FastAPI Backend starting up...")
logger.info(f"📊 Database connected: {engine.url}")
logger.info(f"🔧 GCP AI enabled: {os.getenv('GCP_AI_ENABLED', 'false')}")
logger.info(f"🗂️ GCP credentials path: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'not set')}")

# CORS Configuration using Secret Manager
from app.integrations.gcp.secrets import get_allowed_origins

allowed_origins_str = get_allowed_origins()
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

logger.info(f"✅ Configured CORS origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Market Research Backend API", "version": "1.0.0"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    """Hello endpoint for testing"""
    return {"message": f"Hello {name}"}


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}
