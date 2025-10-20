"""Pydantic schemas for request/response validation."""

# User schemas
from app.schemas.user import User, UserCreate, UserUpdate

# Survey schemas
from app.schemas.survey import (
    Response,
    ResponseCreate,
    Submission,
    SubmissionCreate,
    SubmissionUpdate,
    Survey,
    SurveyCreate,
    SurveyUpdate,
    SurveyQuestion,
)

# Media schemas
from app.schemas.media import Media, MediaCreate, MediaUpdate

# Reporting schemas
from app.schemas.reporting import ChartData, ReportingData, DemographicData, QuestionResponseData

# Settings schemas
from app.schemas.settings import (
    ReportSettings,
    ReportSettingsCreate,
    ReportSettingsUpdate,
    QuestionDisplayName,
    QuestionDisplayNameCreate,
    QuestionDisplayNameUpdate,
    AgeRange,
)

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    # Survey
    "Survey",
    "SurveyCreate",
    "SurveyUpdate",
    "SurveyQuestion",
    "Submission",
    "SubmissionCreate",
    "SubmissionUpdate",
    "Response",
    "ResponseCreate",
    # Media
    "Media",
    "MediaCreate",
    "MediaUpdate",
    # Reporting
    "ReportingData",
    "ChartData",
    "DemographicData",
    "QuestionResponseData",
    # Settings
    "ReportSettings",
    "ReportSettingsCreate",
    "ReportSettingsUpdate",
    "QuestionDisplayName",
    "QuestionDisplayNameCreate",
    "QuestionDisplayNameUpdate",
    "AgeRange",
]
