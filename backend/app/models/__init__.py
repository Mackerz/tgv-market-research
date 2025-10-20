"""SQLAlchemy models for database tables."""

# Import all models to ensure they're registered with SQLAlchemy
from app.models.media import Media  # noqa: F401
from app.models.settings import ReportSettings, QuestionDisplayName  # noqa: F401
from app.models.survey import Survey, Submission, Response  # noqa: F401
from app.models.user import User, Post  # noqa: F401

__all__ = [
    # User models
    "User",
    "Post",
    # Survey models
    "Survey",
    "Submission",
    "Response",
    # Media models
    "Media",
    # Settings models
    "ReportSettings",
    "QuestionDisplayName",
]
