from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.db_types import ArrayType, JSONType, BigIntegerType
from datetime import datetime, date

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(BigIntegerType, primary_key=True, index=True, autoincrement=True)
    survey_slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    client = Column(String, nullable=True)  # Client name/organization
    survey_flow = Column(JSONType, nullable=False)  # JSON structure defining questions and flow
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Third-party integration redirect URLs
    complete_redirect_url = Column(String, nullable=True)  # Redirect URL when survey is completed
    screenout_redirect_url = Column(String, nullable=True)  # Redirect URL when survey is screened out

    # Relationship to submissions
    submissions = relationship("Submission", back_populates="survey")
    report_settings = relationship("ReportSettings", back_populates="survey", uselist=False)
    reporting_labels = relationship("ReportingLabel", back_populates="survey")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(BigIntegerType, primary_key=True, index=True, autoincrement=True)
    survey_id = Column(BigIntegerType, ForeignKey("surveys.id"), nullable=False, index=True)

    # Personal information
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    region = Column(String, nullable=False)  # e.g., "UK", "US", etc.
    date_of_birth = Column(String, nullable=False)  # Stored as string in format "YYYY-MM-DD"
    gender = Column(String, nullable=False)  # "Male", "Female", "I'd rather not say"

    # Submission metadata
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    is_approved = Column(Boolean, nullable=True, default=None)  # None=pending, True=approved, False=rejected
    is_completed = Column(Boolean, default=False)
    age = Column(Integer, nullable=True)  # Calculated age at submission time

    # Third-party integration
    external_user_id = Column(String, nullable=True, index=True)  # Optional third-party user ID

    # Relationships
    survey = relationship("Survey", back_populates="submissions")
    responses = relationship("Response", back_populates="submission")

    # Composite indexes for frequently queried combinations
    __table_args__ = (
        Index('ix_submission_survey_approved', 'survey_id', 'is_approved'),
        Index('ix_submission_survey_completed', 'survey_id', 'is_completed'),
        Index('ix_submission_survey_approved_completed', 'survey_id', 'is_approved', 'is_completed'),
        Index('ix_submission_demographics', 'survey_id', 'region', 'gender'),
    )

    @hybrid_property
    def calculated_age(self):
        """Calculate age based on date_of_birth and submitted_at"""
        if not self.date_of_birth or not self.submitted_at:
            return None

        try:
            birth_date = datetime.strptime(self.date_of_birth, "%Y-%m-%d").date()
            submission_date = self.submitted_at.date()

            # Calculate age in years
            age = submission_date.year - birth_date.year

            # Adjust if birthday hasn't occurred yet this year
            if (submission_date.month, submission_date.day) < (birth_date.month, birth_date.day):
                age -= 1

            return age
        except (ValueError, AttributeError):
            return None

class Response(Base):
    __tablename__ = "responses"

    id = Column(BigIntegerType, primary_key=True, index=True, autoincrement=True)
    submission_id = Column(BigIntegerType, ForeignKey("submissions.id"), nullable=False, index=True)

    # Question information
    question_id = Column(String, nullable=True)  # Question ID from survey_flow (for routing)
    question = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # "free_text", "single", "multi", "photo", "video"

    # Different answer types - only one will be populated based on question_type
    single_answer = Column(Text, nullable=True)  # For single choice and free text
    free_text_answer = Column(Text, nullable=True)  # For free text responses
    multiple_choice_answer = Column(ArrayType, nullable=True)  # For multiple choice
    photo_url = Column(Text, nullable=True)  # GCP storage URL for photos
    video_url = Column(Text, nullable=True)  # GCP storage URL for videos
    video_thumbnail_url = Column(Text, nullable=True)  # Thumbnail URL (future use)

    # Metadata
    responded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    submission = relationship("Submission", back_populates="responses")
    media_analysis = relationship("Media", back_populates="response")

    # Composite index for filtering by submission and question type
    __table_args__ = (
        Index('ix_response_submission_type', 'submission_id', 'question_type'),
    )