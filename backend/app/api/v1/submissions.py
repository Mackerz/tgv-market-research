"""Survey Submission and Response API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.core.database import get_db
from app.schemas import survey as survey_schemas
from app.crud import survey as survey_crud
from app.dependencies import (
    get_survey_or_404,
    get_submission_or_404,
    validate_survey_active,
    validate_submission_not_completed
)
from app.core.rate_limits import get_rate_limit
from app.core.auth import RequireAPIKey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["submissions", "responses"])
limiter = Limiter(key_func=get_remote_address)

# Import centralized background task function (removes duplication)
from app.services.media_analysis import analyze_media_content_background


# =============================================================================
# SUBMISSION ENDPOINTS
# =============================================================================

@router.post("/surveys/{survey_slug}/submit", response_model=survey_schemas.Submission)
@limiter.limit(get_rate_limit("submission_create"))
def create_submission(request: Request, survey_slug: str, submission_data: survey_schemas.SubmissionPersonalInfo, db: Session = Depends(get_db)):
    """Create a new submission for a survey (Rate limit: 30/minute)"""
    # Get survey using dependency helper and validate it's active
    survey = get_survey_or_404(survey_slug, db)
    validate_survey_active(survey)

    # Create submission
    submission = survey_schemas.SubmissionCreate(
        survey_id=survey.id,
        **submission_data.dict()
    )
    return survey_crud.create_submission(db=db, submission_data=submission)


@router.get("/submissions/{submission_id}", response_model=survey_schemas.SubmissionWithResponses)
def read_submission(submission_id: int, db: Session = Depends(get_db)):
    """
    Get a specific submission by ID

    NOTE: This endpoint is public to allow survey takers to view their own submission.
    In production, you may want to add session-based authentication to ensure users
    can only view their own submissions.
    """
    # Get submission using dependency helper
    return get_submission_or_404(submission_id, db)


@router.get("/surveys/{survey_id}/submissions", response_model=List[survey_schemas.Submission])
def read_survey_submissions(
    survey_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = RequireAPIKey
):
    """Get all submissions for a survey (ADMIN ONLY - Requires: X-API-Key header)"""
    submissions = survey_crud.get_submissions_by_survey(db, survey_id=survey_id, skip=skip, limit=limit)
    return submissions


@router.put("/submissions/{submission_id}/complete")
def complete_submission(submission_id: int, db: Session = Depends(get_db)):
    """Mark a submission as completed"""
    # Verify submission exists using dependency helper
    get_submission_or_404(submission_id, db)

    # Mark as completed
    db_submission = survey_crud.mark_submission_completed(db, submission_id)
    return {"message": "Submission marked as completed"}


@router.get("/submissions/{submission_id}/progress", response_model=survey_schemas.SurveyProgress)
def get_submission_progress(submission_id: int, db: Session = Depends(get_db)):
    """Get progress information for a submission"""
    progress = survey_crud.get_survey_progress(db, submission_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Submission not found")
    return progress


# =============================================================================
# RESPONSE ENDPOINTS
# =============================================================================

@router.post("/submissions/{submission_id}/responses", response_model=survey_schemas.Response)
@limiter.limit(get_rate_limit("response_create"))
def create_response(request: Request, submission_id: int, response: survey_schemas.ResponseCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a response for a submission (Rate limit: 50/minute)"""
    # Verify submission exists and is not completed using dependency helpers
    submission = get_submission_or_404(submission_id, db)
    validate_submission_not_completed(submission)

    # Create response with submission_id
    response_create = survey_schemas.ResponseCreate(
        submission_id=submission_id,
        **response.dict(exclude_unset=True)
    )

    created_response = survey_crud.create_response(db=db, response_data=response_create)

    # Trigger AI analysis for photo/video responses
    if response.question_type == "photo" and response.photo_url:
        logger.info(f"📷 Queueing photo analysis for response {created_response.id}: {response.photo_url}")
        background_tasks.add_task(analyze_media_content_background, created_response.id, db)
    elif response.question_type == "video" and response.video_url:
        logger.info(f"🎥 Queueing video analysis for response {created_response.id}: {response.video_url}")
        background_tasks.add_task(analyze_media_content_background, created_response.id, db)
    else:
        logger.info(f"📝 Response {created_response.id} - no media to analyze (type: {response.question_type})")

    return created_response


@router.get("/submissions/{submission_id}/responses", response_model=List[survey_schemas.Response])
def read_submission_responses(submission_id: int, db: Session = Depends(get_db)):
    """Get all responses for a submission"""
    responses = survey_crud.get_responses_by_submission(db, submission_id=submission_id)
    return responses
