"""FastAPI application entry point"""
import logging
import os

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import api_router
from app.core.database import Base, engine, get_db
from app.core.error_handlers import register_error_handlers

# Import models to ensure they're registered with SQLAlchemy

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

# Initialize rate limiter
# This limits requests by IP address to prevent abuse
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Create FastAPI application with request size limits
app = FastAPI(
    title="Market Research Backend API",
    version="1.0.0",
    description="Backend API for Market Research Survey Platform"
)

# Add request size limit middleware (50MB for file uploads, 10MB for regular requests)
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request size limits."""
    async def dispatch(self, request: Request, call_next):
        # Check if this is a file upload endpoint
        is_upload = "/upload" in request.url.path or "/media" in request.url.path
        max_size = 52428800 if is_upload else 10485760  # 50MB for uploads, 10MB for others

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_size:
            max_mb = max_size / 1048576
            raise StarletteHTTPException(
                status_code=413,
                detail=f"Request body too large. Maximum allowed: {max_mb}MB"
            )

        return await call_next(request)

# Add request size limit middleware
app.add_middleware(RequestSizeLimitMiddleware)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register centralized error handlers
register_error_handlers(app)

# Log startup information
logger.info("🚀 FastAPI Backend starting up...")
logger.info(f"📊 Database connected: {engine.url}")
logger.info(f"🔧 GCP AI enabled: {os.getenv('GCP_AI_ENABLED', 'false')}")
logger.info(f"🗂️ GCP credentials path: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'not set')}")

# CORS Configuration
from app.integrations.gcp.secrets import get_allowed_origins

# Check if ALLOWED_ORIGINS is explicitly set in environment (for local Docker/dev)
allowed_origins_str = os.getenv("ALLOWED_ORIGINS")

if not allowed_origins_str:
    # Try to get from GCP Secret Manager (for production)
    try:
        allowed_origins_str = get_allowed_origins()
        logger.info("✅ CORS origins retrieved from GCP Secret Manager")
    except Exception as e:
        logger.error(f"❌ Failed to get CORS origins from GCP: {e}")
        # Final fallback for local development
        allowed_origins_str = "http://localhost:3000"
        logger.warning(f"⚠️ Using default CORS origin: {allowed_origins_str}")
else:
    logger.info("✅ CORS origins loaded from environment variable")

allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
logger.info(f"✅ Configured CORS origins: {allowed_origins}")

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: Prevents MIME-type sniffing
    - X-Frame-Options: Prevents clickjacking attacks
    - X-XSS-Protection: Enables browser XSS filter
    - Strict-Transport-Security: Enforces HTTPS
    - Content-Security-Policy: Restricts resource loading
    - Referrer-Policy: Controls referrer information
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS (only in production)
        if os.getenv("ENVIRONMENT", "development") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy - strict by default
        # Allow same-origin content and specified domains
        csp_directives = [
            "default-src 'self'",
            "img-src 'self' data: https://storage.googleapis.com",
            "media-src 'self' https://storage.googleapis.com",
            "script-src 'self' 'unsafe-inline'",  # Allow inline scripts for Swagger UI
            "style-src 'self' 'unsafe-inline'",   # Allow inline styles for Swagger UI
            "connect-src 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response

# Add Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # More restrictive than "*"
    allow_headers=["Content-Type", "Authorization"],  # More restrictive than "*"
)

logger.info("🔒 Security headers middleware enabled")
logger.info("🔒 CORS middleware configured with restricted methods and headers")
logger.info("🚦 Rate limiting enabled: 100 requests/minute per IP (default)")

# Include API router
app.include_router(api_router)


# =============================================================================
# STARTUP/SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_validation():
    """
    Validate configuration and dependencies on startup.

    This ensures the application fails fast if critical
    configuration is missing or invalid.
    """
    logger.info("🔍 Running startup validation...")

    errors = []

    # 1. Check database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection validated")
    except Exception as e:
        error_msg = f"Database connection failed: {e}"
        logger.error(f"❌ {error_msg}")
        errors.append(error_msg)

    # 2. Check required environment variables
    required_env_vars = {
        "DATABASE_URL": "Database connection string",
        "GCP_PROJECT_ID": "GCP project identifier",
    }

    for var_name, description in required_env_vars.items():
        value = os.getenv(var_name)
        if not value:
            error_msg = f"Missing required environment variable: {var_name} ({description})"
            logger.error(f"❌ {error_msg}")
            errors.append(error_msg)
        else:
            # Mask sensitive values in logs
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
            logger.info(f"✅ {var_name}: {masked_value}")

    # 3. Check GCP credentials (if AI enabled)
    gcp_ai_enabled = os.getenv("GCP_AI_ENABLED", "false").lower() == "true"
    if gcp_ai_enabled:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path:
            if not os.path.exists(credentials_path):
                error_msg = f"GCP credentials file not found: {credentials_path}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
            else:
                logger.info("✅ GCP credentials file found")
        else:
            logger.warning("⚠️ GCP_AI_ENABLED=true but GOOGLE_APPLICATION_CREDENTIALS not set")
            logger.warning("⚠️ Will attempt to use Application Default Credentials")

    # 4. Check GCP buckets configuration
    if gcp_ai_enabled:
        photo_bucket = os.getenv("GCP_STORAGE_BUCKET_PHOTOS")
        video_bucket = os.getenv("GCP_STORAGE_BUCKET_VIDEOS")

        if not photo_bucket:
            logger.warning("⚠️ GCP_STORAGE_BUCKET_PHOTOS not set")
        else:
            logger.info(f"✅ Photos bucket: {photo_bucket}")

        if not video_bucket:
            logger.warning("⚠️ GCP_STORAGE_BUCKET_VIDEOS not set")
        else:
            logger.info(f"✅ Videos bucket: {video_bucket}")

    # 5. Check CORS configuration
    if not allowed_origins or allowed_origins == [""]:
        logger.warning("⚠️ No CORS origins configured - API may not be accessible from frontend")
    else:
        logger.info(f"✅ CORS configured for {len(allowed_origins)} origin(s)")

    # If any critical errors, raise exception to prevent startup
    if errors:
        error_summary = "\n".join(f"  - {err}" for err in errors)
        raise RuntimeError(
            f"❌ Application startup failed due to configuration errors:\n{error_summary}"
        )

    logger.info("✅ All startup validations passed")
    logger.info("🚀 Application is ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Application shutting down...")
    logger.info("🔌 Closing database connections...")


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
