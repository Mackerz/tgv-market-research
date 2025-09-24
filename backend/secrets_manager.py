"""
Google Secret Manager utility for TMG Market Research
Handles retrieval of secrets from Google Cloud Secret Manager
"""

import os
import logging
from typing import Optional

# Try to import Google Cloud dependencies, but continue without them if not available
try:
    from google.cloud import secretmanager
    from google.api_core.exceptions import NotFound, PermissionDenied
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    secretmanager = None
    NotFound = Exception
    PermissionDenied = Exception

logger = logging.getLogger(__name__)

class SecretsManager:
    """Helper class for Google Cloud Secret Manager operations"""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.client = None

        if self.project_id and GOOGLE_CLOUD_AVAILABLE:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
                logger.info(f"✅ Secret Manager client initialized for project: {self.project_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Secret Manager client: {e}")
                logger.info("Falling back to environment variables")
        elif not GOOGLE_CLOUD_AVAILABLE:
            logger.info("Google Cloud libraries not available, using environment variables only")
        else:
            logger.info("No GCP_PROJECT_ID found, using environment variables only")

    def get_secret(self, secret_name: str, fallback_env_var: str = None) -> Optional[str]:
        """
        Get a secret from Secret Manager with fallback to environment variables

        Args:
            secret_name: Name of the secret in Secret Manager
            fallback_env_var: Environment variable name to use as fallback

        Returns:
            Secret value or None if not found
        """
        # First try Secret Manager
        if self.client and self.project_id:
            try:
                name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                response = self.client.access_secret_version(request={"name": name})
                secret_value = response.payload.data.decode("UTF-8")
                logger.debug(f"✅ Retrieved secret '{secret_name}' from Secret Manager")
                return secret_value

            except NotFound:
                logger.warning(f"⚠️ Secret '{secret_name}' not found in Secret Manager")
            except PermissionDenied:
                logger.warning(f"⚠️ Permission denied accessing secret '{secret_name}'")
            except Exception as e:
                logger.warning(f"⚠️ Error accessing secret '{secret_name}': {e}")

        # Fallback to environment variables
        if fallback_env_var:
            env_value = os.getenv(fallback_env_var)
            if env_value:
                logger.debug(f"✅ Using environment variable '{fallback_env_var}' as fallback")
                return env_value
            else:
                logger.warning(f"⚠️ Environment variable '{fallback_env_var}' not found")

        # Try the secret name as env var if no specific fallback provided
        env_value = os.getenv(secret_name.upper().replace("-", "_"))
        if env_value:
            logger.debug(f"✅ Using environment variable '{secret_name.upper().replace('-', '_')}'")
            return env_value

        logger.error(f"❌ Failed to retrieve secret '{secret_name}' from both Secret Manager and environment variables")
        return None

# Global instance
secrets_manager = SecretsManager()

def get_database_url() -> str:
    """Get database URL from secrets or environment"""
    database_url = secrets_manager.get_secret("database-url", "DATABASE_URL")
    if not database_url:
        # Construct from individual components if direct URL not available
        db_host = secrets_manager.get_secret("db-host", "DB_HOST")
        db_port = secrets_manager.get_secret("db-port", "DB_PORT") or "5432"
        db_name = secrets_manager.get_secret("db-name", "DB_NAME") or "market_research"
        db_user = secrets_manager.get_secret("db-user", "DB_USER") or "app_user"
        db_password = secrets_manager.get_secret("db-password", "DB_PASSWORD")

        if db_host and db_password:
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            logger.info("✅ Constructed database URL from individual secret components")
        else:
            raise ValueError("❌ Could not construct database URL: missing host or password")

    return database_url

def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from secrets or environment"""
    return secrets_manager.get_secret("gemini-api-key", "GEMINI_API_KEY")

def get_gcp_project_id() -> Optional[str]:
    """Get GCP project ID from secrets or environment"""
    return secrets_manager.get_secret("gcp-project-id", "GCP_PROJECT_ID")

def get_gcs_bucket_name() -> Optional[str]:
    """Get GCS bucket name from secrets or environment"""
    return secrets_manager.get_secret("gcs-bucket-name", "GCS_BUCKET_NAME")

def get_allowed_origins() -> str:
    """Get allowed CORS origins from secrets or environment"""
    return secrets_manager.get_secret("allowed-origins", "ALLOWED_ORIGINS") or "http://localhost:3000"