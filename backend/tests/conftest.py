"""Pytest configuration and fixtures for backend tests"""
import os
import pytest

# Set test environment variables BEFORE importing any app modules
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["GCP_AI_ENABLED"] = "false"
os.environ["GCP_PROJECT_ID"] = ""  # Disable GCP to avoid credential checks
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
os.environ["GCS_PHOTO_BUCKET"] = "test-photos"
os.environ["GCS_VIDEO_BUCKET"] = "test-videos"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"  # Avoid secret manager call

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.models import user as models
from app.models import survey as survey_models
from app.models import media as media_models
from app.models import settings as settings_models


@pytest.fixture(scope="function")
def db_engine():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a database session for testing"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_survey(db_session):
    """Create a sample survey for testing"""
    survey = survey_models.Survey(
        survey_slug="test-survey-123",
        name="Test Survey",
        survey_flow=[
            {
                "id": "q1",
                "question": "What is your favorite color?",
                "question_type": "single",
                "answers": ["Red", "Blue", "Green"]
            },
            {
                "id": "q2",
                "question": "Select all that apply",
                "question_type": "multi",
                "answers": ["Option 1", "Option 2", "Option 3"]
            }
        ],
        is_active=True
    )
    db_session.add(survey)
    db_session.commit()
    db_session.refresh(survey)
    return survey


@pytest.fixture
def sample_submission(db_session, sample_survey):
    """Create a sample submission for testing"""
    submission = survey_models.Submission(
        survey_id=sample_survey.id,
        email="test@example.com",
        phone_number="1234567890",
        region="North America",
        date_of_birth="1990-01-01",
        gender="Male",
        is_completed=True,
        is_approved=True
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    return submission


@pytest.fixture
def sample_response(db_session, sample_submission):
    """Create a sample response for testing"""
    response = survey_models.Response(
        submission_id=sample_submission.id,
        question="What is your favorite color?",
        question_type="single",
        single_answer="Blue"
    )
    db_session.add(response)
    db_session.commit()
    db_session.refresh(response)
    return response


@pytest.fixture
def sample_media_analysis(db_session, sample_response):
    """Create a sample media analysis for testing"""
    media = media_models.Media(
        response_id=sample_response.id,
        description="Test image description",
        reporting_labels='["label1", "label2", "label3"]',
        brands_detected='["Brand A", "Brand B"]'
    )
    db_session.add(media)
    db_session.commit()
    db_session.refresh(media)
    return media


@pytest.fixture
def multiple_submissions(db_session, sample_survey):
    """Create multiple submissions with different approval statuses"""
    submissions = []

    # Approved submission
    sub1 = survey_models.Submission(
        survey_id=sample_survey.id,
        email="approved@example.com",
        phone_number="1111111111",
        region="North America",
        date_of_birth="1990-01-01",
        gender="Male",
        is_completed=True,
        is_approved=True
    )
    submissions.append(sub1)

    # Rejected submission
    sub2 = survey_models.Submission(
        survey_id=sample_survey.id,
        email="rejected@example.com",
        phone_number="2222222222",
        region="Europe",
        date_of_birth="1995-01-01",
        gender="Female",
        is_completed=True,
        is_approved=False
    )
    submissions.append(sub2)

    # Pending submission
    sub3 = survey_models.Submission(
        survey_id=sample_survey.id,
        email="pending@example.com",
        phone_number="3333333333",
        region="Asia",
        date_of_birth="1985-01-01",
        gender="Male",
        is_completed=True,
        is_approved=None
    )
    submissions.append(sub3)

    # Incomplete submission
    sub4 = survey_models.Submission(
        survey_id=sample_survey.id,
        email="incomplete@example.com",
        phone_number="4444444444",
        region="South America",
        date_of_birth="2000-01-01",
        gender="Female",
        is_completed=False,
        is_approved=None
    )
    submissions.append(sub4)

    for sub in submissions:
        db_session.add(sub)

    db_session.commit()

    for sub in submissions:
        db_session.refresh(sub)

    return submissions
