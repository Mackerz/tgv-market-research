"""Survey, Submission, and Response CRUD operations using CRUDBase"""
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc
from typing import List, Optional
import uuid
import secrets
import string

from app.crud.base import CRUDBase
from app.models.survey import Survey, Submission, Response
from app.schemas.survey import (
    SurveyCreate,
    SurveyUpdate,
    SubmissionCreate,
    SubmissionUpdate,
    ResponseCreate,
    ResponseUpdate,
    SurveyProgress,
)
from app.utils.validation import sanitize_user_input


# Helper function to generate survey slug
def generate_survey_slug(length: int = 8) -> str:
    """Generate a unique survey slug similar to Google Meet IDs"""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class CRUDSurvey(CRUDBase[Survey, SurveyCreate, SurveyUpdate]):
    """CRUD operations for Survey model"""

    def get_by_slug(self, db: Session, survey_slug: str) -> Optional[Survey]:
        """Get survey by slug"""
        return db.query(self.model).filter(self.model.survey_slug == survey_slug).first()

    def get_multi_active(
        self, db: Session, *, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Survey]:
        """Get surveys with optional active filter"""
        query = db.query(self.model)
        if active_only:
            query = query.filter(self.model.is_active == True)
        return query.offset(skip).limit(limit).all()

    def copy_survey(self, db: Session, survey_id: int) -> Survey:
        """
        Create a copy of an existing survey with a new unique slug and name.
        The copied survey will have "(Copy)" appended to its name and a new generated slug.
        """
        # Get the original survey
        original_survey = self.get(db, survey_id)
        if not original_survey:
            raise ValueError(f"Survey with ID {survey_id} not found")

        # Generate a unique slug
        new_slug = generate_survey_slug()
        attempts = 0
        max_attempts = 10
        while self.get_by_slug(db, new_slug) and attempts < max_attempts:
            new_slug = generate_survey_slug()
            attempts += 1

        if attempts >= max_attempts:
            raise ValueError("Failed to generate a unique survey slug")

        # Create new survey name
        new_name = f"{original_survey.name} (Copy)"

        # Create the new survey
        db_obj = self.model(
            survey_slug=new_slug,
            name=new_name,
            survey_flow=original_survey.survey_flow,  # Deep copy of JSON
            is_active=False,  # Start as inactive
            client=original_survey.client,
            complete_redirect_url=original_survey.complete_redirect_url,
            screenout_redirect_url=original_survey.screenout_redirect_url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create(self, db: Session, *, obj_in: SurveyCreate) -> Survey:
        """Create survey with unique slug validation"""
        # Check if slug already exists
        existing_survey = self.get_by_slug(db, obj_in.survey_slug)
        if existing_survey:
            from sqlalchemy.exc import IntegrityError
            raise IntegrityError(
                f"Survey with slug '{obj_in.survey_slug}' already exists",
                params=None,
                orig=None
            )

        # Convert Pydantic models to dict for JSON storage
        survey_flow_dict = [q.dict() for q in obj_in.survey_flow]

        db_obj = self.model(
            survey_slug=obj_in.survey_slug,
            name=obj_in.name,
            survey_flow=survey_flow_dict,
            is_active=obj_in.is_active,
            client=obj_in.client if hasattr(obj_in, 'client') else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Survey, obj_in: SurveyUpdate | dict
    ) -> Survey:
        """Update survey with survey_flow conversion"""
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in

        # Convert survey_flow to dict if present
        if 'survey_flow' in update_data and update_data['survey_flow']:
            # Handle both Pydantic models and dicts
            survey_flow = update_data['survey_flow']
            if survey_flow and len(survey_flow) > 0:
                # Check if first item is a dict or Pydantic model
                if hasattr(survey_flow[0], 'dict'):
                    update_data['survey_flow'] = [q.dict() for q in survey_flow]
                # If it's already a dict, leave it as is

        return super().update(db, db_obj=db_obj, obj_in=update_data)


class CRUDSubmission(CRUDBase[Submission, SubmissionCreate, SubmissionUpdate]):
    """CRUD operations for Submission model"""

    def get_multi_by_survey(
        self, db: Session, *, survey_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """
        Get submissions by survey.

        Uses selectinload to eagerly load responses relationship
        to prevent N+1 queries.
        """
        return (
            db.query(self.model)
            .options(selectinload(self.model.responses))
            .filter(self.model.survey_id == survey_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_survey_with_media(
        self, db: Session, *, survey_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """
        Get submissions by survey with responses and media analysis eager loaded.

        Uses nested selectinload to prevent N+1 queries when accessing
        submission.responses[*].media_analysis relationships.

        This is optimized for endpoints that need full submission data
        including media analysis (e.g., reporting, media summaries).
        """
        return (
            db.query(self.model)
            .options(
                selectinload(self.model.responses).selectinload(
                    Response.media_analysis
                )
            )
            .filter(self.model.survey_id == survey_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get submissions ordered by submitted_at"""
        return (
            db.query(self.model)
            .order_by(desc(self.model.submitted_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: SubmissionCreate) -> Submission:
        """Create submission with age calculation"""
        db_obj = self.model(
            survey_id=obj_in.survey_id,
            email=obj_in.email,
            phone_number=obj_in.phone_number,
            region=obj_in.region,
            date_of_birth=obj_in.date_of_birth,
            gender=obj_in.gender,
            is_approved=None,  # Starts as pending (to be approved)
            is_completed=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Calculate and store age after submission is created and has a submitted_at timestamp
        if db_obj.calculated_age is not None:
            db_obj.age = db_obj.calculated_age
            db.commit()
            db.refresh(db_obj)

        return db_obj

    def mark_completed(self, db: Session, submission_id: int) -> Optional[Submission]:
        """Mark submission as completed"""
        return self.update_by_id(db, id=submission_id, obj_in=SubmissionUpdate(is_completed=True))


class CRUDResponse(CRUDBase[Response, ResponseCreate, ResponseUpdate]):
    """CRUD operations for Response model"""

    def get_multi_by_submission(
        self, db: Session, *, submission_id: int
    ) -> List[Response]:
        """
        Get responses by submission, ordered by responded_at.

        Uses selectinload to eagerly load media_analysis relationship
        to prevent N+1 queries.
        """
        return (
            db.query(self.model)
            .options(selectinload(self.model.media_analysis))
            .filter(self.model.submission_id == submission_id)
            .order_by(self.model.responded_at)
            .all()
        )

    def create(self, db: Session, *, obj_in: ResponseCreate) -> Response:
        """Create response with input sanitization"""
        # Sanitize user text inputs to prevent XSS attacks
        sanitized_single_answer = None
        if obj_in.single_answer:
            sanitized_single_answer = sanitize_user_input(obj_in.single_answer, max_length=500)

        sanitized_free_text = None
        if obj_in.free_text_answer:
            sanitized_free_text = sanitize_user_input(obj_in.free_text_answer, max_length=2000)

        db_obj = self.model(
            submission_id=obj_in.submission_id,
            question=obj_in.question,
            question_type=obj_in.question_type,
            single_answer=sanitized_single_answer,
            free_text_answer=sanitized_free_text,
            multiple_choice_answer=obj_in.multiple_choice_answer,
            photo_url=obj_in.photo_url,
            video_url=obj_in.video_url,
            video_thumbnail_url=obj_in.video_thumbnail_url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create singleton instances
survey = CRUDSurvey(Survey)
submission = CRUDSubmission(Submission)
response = CRUDResponse(Response)


# Backward compatibility - maintain old function signatures
# Survey functions
def get_survey(db: Session, survey_id: int) -> Optional[Survey]:
    """Get survey by ID"""
    return survey.get(db, survey_id)


def get_survey_by_slug(db: Session, survey_slug: str) -> Optional[Survey]:
    """Get survey by slug"""
    return survey.get_by_slug(db, survey_slug)


def get_surveys(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Survey]:
    """Get surveys"""
    return survey.get_multi_active(db, skip=skip, limit=limit, active_only=active_only)


def create_survey(db: Session, survey_data: SurveyCreate) -> Survey:
    """Create survey"""
    return survey.create(db, obj_in=survey_data)


def update_survey(db: Session, survey_id: int, survey_data: SurveyUpdate) -> Optional[Survey]:
    """Update survey"""
    return survey.update_by_id(db, id=survey_id, obj_in=survey_data)


def delete_survey(db: Session, survey_id: int) -> bool:
    """Delete survey"""
    return survey.delete(db, id=survey_id)


def copy_survey(db: Session, survey_id: int) -> Survey:
    """Copy survey"""
    return survey.copy_survey(db, survey_id)


# Submission functions
def get_submission(db: Session, submission_id: int) -> Optional[Submission]:
    """Get submission by ID"""
    return submission.get(db, submission_id)


def get_submissions_by_survey(db: Session, survey_id: int, skip: int = 0, limit: int = 100) -> List[Submission]:
    """Get submissions by survey"""
    return submission.get_multi_by_survey(db, survey_id=survey_id, skip=skip, limit=limit)


def get_submissions(db: Session, skip: int = 0, limit: int = 100) -> List[Submission]:
    """Get all submissions"""
    return submission.get_multi(db, skip=skip, limit=limit)


def create_submission(db: Session, submission_data: SubmissionCreate) -> Submission:
    """Create submission"""
    return submission.create(db, obj_in=submission_data)


def update_submission(db: Session, submission_id: int, submission_data: SubmissionUpdate) -> Optional[Submission]:
    """Update submission"""
    return submission.update_by_id(db, id=submission_id, obj_in=submission_data)


def mark_submission_completed(db: Session, submission_id: int) -> Optional[Submission]:
    """Mark submission as completed"""
    return submission.mark_completed(db, submission_id)


# Response functions
def get_response(db: Session, response_id: int) -> Optional[Response]:
    """Get response by ID"""
    return response.get(db, response_id)


def get_responses_by_submission(db: Session, submission_id: int) -> List[Response]:
    """Get responses by submission"""
    return response.get_multi_by_submission(db, submission_id=submission_id)


def create_response(db: Session, response_data: ResponseCreate) -> Response:
    """Create response"""
    return response.create(db, obj_in=response_data)


def update_response(db: Session, response_id: int, response_data: ResponseUpdate) -> Optional[Response]:
    """Update response"""
    return response.update_by_id(db, id=response_id, obj_in=response_data)


# Survey progress helper
def get_survey_progress(db: Session, submission_id: int) -> Optional[SurveyProgress]:
    """Get survey progress for a submission"""
    db_submission = get_submission(db, submission_id)
    if not db_submission:
        return None

    db_survey = get_survey(db, db_submission.survey_id)
    if not db_survey:
        return None

    responses = get_responses_by_submission(db, submission_id)

    return SurveyProgress(
        current_question=len(responses),
        total_questions=len(db_survey.survey_flow),
        submission_id=submission_id,
        is_completed=db_submission.is_completed
    )


# File handling helper functions
def generate_file_id() -> str:
    """Generate a unique file ID for GCP storage"""
    return str(uuid.uuid4())


def build_gcp_storage_path(survey_slug: str, file_id: str, file_extension: str) -> str:
    """Build GCP storage path: gcp_bucket_for_photo_or_video/survey_slug/unique_id.ext"""
    return f"survey-uploads/{survey_slug}/{file_id}.{file_extension}"
