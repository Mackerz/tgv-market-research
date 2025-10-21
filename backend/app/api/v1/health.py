"""Health check and system status endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.auth import RequireAPIKey
from app.core.csrf import generate_csrf_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    """
    Basic health check endpoint - returns 200 if the service is running.
    Use this for container health checks and load balancer health probes.
    Also provides CSRF token for frontend applications.
    """
    csrf_enabled = os.getenv("CSRF_PROTECTION_ENABLED", "false").lower() == "true"

    response = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "TMG Market Research API"
    }

    # Include CSRF token if protection is enabled
    if csrf_enabled:
        response["csrf_token"] = generate_csrf_token()

    return response


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check - verifies the service is ready to handle requests.
    Checks database connectivity and essential dependencies.
    """
    checks = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        checks["checks"]["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        checks["status"] = "not_ready"
        checks["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        logger.error(f"Database health check failed: {str(e)}")

    # Check GCP credentials
    gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_creds and os.path.exists(gcp_creds):
        checks["checks"]["gcp_credentials"] = {
            "status": "healthy",
            "message": "Credentials file exists"
        }
    else:
        checks["checks"]["gcp_credentials"] = {
            "status": "warning",
            "message": "GCP credentials not configured or file not found"
        }

    # Check GCS bucket configuration
    gcs_bucket = os.getenv("GCS_BUCKET_NAME")
    if gcs_bucket:
        checks["checks"]["gcs_bucket"] = {
            "status": "healthy",
            "message": f"Bucket configured: {gcs_bucket}"
        }
    else:
        checks["checks"]["gcs_bucket"] = {
            "status": "warning",
            "message": "GCS bucket not configured"
        }

    # Return 503 if not ready
    if checks["status"] != "ready":
        raise HTTPException(status_code=503, detail=checks)

    return checks


@router.get("/health/live")
def liveness_check():
    """
    Liveness check - verifies the service is alive and not deadlocked.
    This is a simple endpoint that should always return 200 unless the service is completely down.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db), api_key: str = RequireAPIKey):
    """
    Detailed health check with comprehensive system information.
    Requires authentication as it exposes sensitive configuration details.
    (ADMIN ONLY - Requires: X-API-Key header)
    """
    from app.integrations.gcp.vision import gcp_ai_analyzer
    from app.integrations.gcp.gemini import gemini_labeler

    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "TMG Market Research API",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "checks": {}
    }

    # Database check with connection pool info
    try:
        db.execute(text("SELECT 1"))
        from app.core.database import engine
        pool = engine.pool
        checks["checks"]["database"] = {
            "status": "healthy",
            "connection": "Connected",
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_in": pool.checkedin()
        }
    except Exception as e:
        checks["status"] = "degraded"
        checks["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # GCP AI services
    checks["checks"]["gcp_vision"] = {
        "status": "healthy" if gcp_ai_analyzer.enabled else "disabled",
        "vision_client": gcp_ai_analyzer.vision_client is not None,
        "video_client": gcp_ai_analyzer.video_client is not None
    }

    checks["checks"]["gemini"] = {
        "status": "healthy" if gemini_labeler.enabled else "disabled",
        "model_available": gemini_labeler.model is not None
    }

    # Storage
    checks["checks"]["gcs_storage"] = {
        "status": "healthy" if os.getenv("GCS_BUCKET_NAME") else "not_configured",
        "bucket": os.getenv("GCS_BUCKET_NAME", "not_set")
    }

    # Authentication
    checks["checks"]["authentication"] = {
        "status": "healthy" if os.getenv("API_KEY") else "disabled",
        "api_key_configured": bool(os.getenv("API_KEY"))
    }

    # Environment variables
    checks["checks"]["environment"] = {
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "gcp_project_id": os.getenv("GCP_PROJECT_ID", "not_set"),
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", "not_set"),
        "log_level": os.getenv("LOG_LEVEL", "INFO")
    }

    return checks
