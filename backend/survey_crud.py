from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
import survey_models
import survey_schemas
import uuid
import secrets
import string

# Helper function to generate survey slug
def generate_survey_slug(length: int = 8) -> str:
    """Generate a unique survey slug similar to Google Meet IDs"""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Survey CRUD operations
def get_survey(db: Session, survey_id: int) -> Optional[survey_models.Survey]:
    return db.query(survey_models.Survey).filter(survey_models.Survey.id == survey_id).first()

def get_survey_by_slug(db: Session, survey_slug: str) -> Optional[survey_models.Survey]:
    return db.query(survey_models.Survey).filter(survey_models.Survey.survey_slug == survey_slug).first()

def get_surveys(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[survey_models.Survey]:
    query = db.query(survey_models.Survey)
    if active_only:
        query = query.filter(survey_models.Survey.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_survey(db: Session, survey: survey_schemas.SurveyCreate) -> survey_models.Survey:
    # Generate unique slug if not provided or if it already exists
    survey_slug = survey.survey_slug
    while get_survey_by_slug(db, survey_slug):
        survey_slug = generate_survey_slug()

    # Convert Pydantic models to dict for JSON storage
    survey_flow_dict = [q.dict() for q in survey.survey_flow]

    db_survey = survey_models.Survey(
        survey_slug=survey_slug,
        name=survey.name,
        survey_flow=survey_flow_dict,
        is_active=survey.is_active
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey

def update_survey(db: Session, survey_id: int, survey: survey_schemas.SurveyUpdate) -> Optional[survey_models.Survey]:
    db_survey = get_survey(db, survey_id)
    if db_survey:
        update_data = survey.dict(exclude_unset=True)

        # Convert survey_flow to dict if present
        if 'survey_flow' in update_data and update_data['survey_flow']:
            update_data['survey_flow'] = [q.dict() for q in update_data['survey_flow']]

        for field, value in update_data.items():
            setattr(db_survey, field, value)
        db.commit()
        db.refresh(db_survey)
    return db_survey

def delete_survey(db: Session, survey_id: int) -> bool:
    db_survey = get_survey(db, survey_id)
    if db_survey:
        db.delete(db_survey)
        db.commit()
        return True
    return False

# Submission CRUD operations
def get_submission(db: Session, submission_id: int) -> Optional[survey_models.Submission]:
    return db.query(survey_models.Submission).filter(survey_models.Submission.id == submission_id).first()

def get_submissions_by_survey(db: Session, survey_id: int, skip: int = 0, limit: int = 100) -> List[survey_models.Submission]:
    return db.query(survey_models.Submission).filter(
        survey_models.Submission.survey_id == survey_id
    ).offset(skip).limit(limit).all()

def get_submissions(db: Session, skip: int = 0, limit: int = 100) -> List[survey_models.Submission]:
    return db.query(survey_models.Submission).order_by(desc(survey_models.Submission.submitted_at)).offset(skip).limit(limit).all()

def create_submission(db: Session, submission: survey_schemas.SubmissionCreate) -> survey_models.Submission:
    db_submission = survey_models.Submission(
        survey_id=submission.survey_id,
        email=submission.email,
        phone_number=submission.phone_number,
        region=submission.region,
        date_of_birth=submission.date_of_birth,
        gender=submission.gender,
        is_approved=False,
        is_completed=False
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    # Calculate and store age after submission is created and has a submitted_at timestamp
    if db_submission.calculated_age is not None:
        db_submission.age = db_submission.calculated_age
        db.commit()
        db.refresh(db_submission)

    return db_submission

def update_submission(db: Session, submission_id: int, submission: survey_schemas.SubmissionUpdate) -> Optional[survey_models.Submission]:
    db_submission = get_submission(db, submission_id)
    if db_submission:
        update_data = submission.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_submission, field, value)
        db.commit()
        db.refresh(db_submission)
    return db_submission

def mark_submission_completed(db: Session, submission_id: int) -> Optional[survey_models.Submission]:
    return update_submission(db, submission_id, survey_schemas.SubmissionUpdate(is_completed=True))

# Response CRUD operations
def get_response(db: Session, response_id: int) -> Optional[survey_models.Response]:
    return db.query(survey_models.Response).filter(survey_models.Response.id == response_id).first()

def get_responses_by_submission(db: Session, submission_id: int) -> List[survey_models.Response]:
    return db.query(survey_models.Response).filter(
        survey_models.Response.submission_id == submission_id
    ).order_by(survey_models.Response.responded_at).all()

def create_response(db: Session, response: survey_schemas.ResponseCreate) -> survey_models.Response:
    # Determine which answer field to populate based on question_type
    db_response = survey_models.Response(
        submission_id=response.submission_id,
        question=response.question,
        question_type=response.question_type,
        single_answer=response.single_answer,
        free_text_answer=response.free_text_answer,
        multiple_choice_answer=response.multiple_choice_answer,
        photo_url=response.photo_url,
        video_url=response.video_url,
        video_thumbnail_url=response.video_thumbnail_url
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

def update_response(db: Session, response_id: int, response: survey_schemas.ResponseUpdate) -> Optional[survey_models.Response]:
    db_response = get_response(db, response_id)
    if db_response:
        update_data = response.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_response, field, value)
        db.commit()
        db.refresh(db_response)
    return db_response

# Survey progress helper
def get_survey_progress(db: Session, submission_id: int) -> Optional[survey_schemas.SurveyProgress]:
    submission = get_submission(db, submission_id)
    if not submission:
        return None

    survey = get_survey(db, submission.survey_id)
    if not survey:
        return None

    responses = get_responses_by_submission(db, submission_id)

    return survey_schemas.SurveyProgress(
        current_question=len(responses),
        total_questions=len(survey.survey_flow),
        submission_id=submission_id,
        is_completed=submission.is_completed
    )

# File handling helper functions
def generate_file_id() -> str:
    """Generate a unique file ID for GCP storage"""
    return str(uuid.uuid4())

def build_gcp_storage_path(survey_slug: str, file_id: str, file_extension: str) -> str:
    """Build GCP storage path: gcp_bucket_for_photo_or_video/survey_slug/unique_id.ext"""
    return f"survey-uploads/{survey_slug}/{file_id}.{file_extension}"