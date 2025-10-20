"""FastAPI dependencies for reusable request handling"""
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import survey as survey_crud
from app.crud import user as user_crud
from app.models import survey as survey_models
from app.models import user as user_models


# =============================================================================
# USER DEPENDENCIES
# =============================================================================

def get_user_or_404(
    user_id: int,
    db: Session = Depends(get_db)
) -> user_models.User:
    """
    Dependency to get user by ID or raise 404

    Args:
        user_id: User ID
        db: Database session

    Returns:
        User model instance

    Raises:
        HTTPException: 404 if user not found
    """
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_post_or_404(
    post_id: int,
    db: Session = Depends(get_db)
) -> user_models.Post:
    """
    Dependency to get post by ID or raise 404

    Args:
        post_id: Post ID
        db: Database session

    Returns:
        Post model instance

    Raises:
        HTTPException: 404 if post not found
    """
    post = user_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# =============================================================================
# SURVEY DEPENDENCIES
# =============================================================================

def get_survey_or_404(
    survey_slug: str,
    db: Session = Depends(get_db)
) -> survey_models.Survey:
    """
    Dependency to get survey by slug or raise 404

    This eliminates repeated code pattern of looking up surveys and checking existence.

    Args:
        survey_slug: Survey slug identifier
        db: Database session

    Returns:
        Survey model instance

    Raises:
        HTTPException: 404 if survey not found
    """
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


def get_survey_by_id_or_404(
    survey_id: int,
    db: Session = Depends(get_db)
) -> survey_models.Survey:
    """
    Dependency to get survey by ID or raise 404

    Args:
        survey_id: Survey ID
        db: Database session

    Returns:
        Survey model instance

    Raises:
        HTTPException: 404 if survey not found
    """
    survey = survey_crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


# =============================================================================
# SUBMISSION DEPENDENCIES
# =============================================================================

def get_submission_or_404(
    submission_id: int,
    db: Session = Depends(get_db)
) -> survey_models.Submission:
    """
    Dependency to get submission by ID or raise 404

    Args:
        submission_id: Submission ID
        db: Database session

    Returns:
        Submission model instance

    Raises:
        HTTPException: 404 if submission not found
    """
    submission = survey_crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


def get_submission_for_survey_or_404(
    survey_slug: str,
    submission_id: int,
    db: Session = Depends(get_db)
) -> tuple[survey_models.Survey, survey_models.Submission]:
    """
    Dependency to get both survey and submission, validating they match

    Args:
        survey_slug: Survey slug
        submission_id: Submission ID
        db: Database session

    Returns:
        Tuple of (Survey, Submission)

    Raises:
        HTTPException: 404 if survey or submission not found, or if they don't match
    """
    survey = get_survey_or_404(survey_slug, db)
    submission = get_submission_or_404(submission_id, db)

    if submission.survey_id != survey.id:
        raise HTTPException(status_code=404, detail="Submission not found")

    return survey, submission


# =============================================================================
# RESPONSE DEPENDENCIES
# =============================================================================

def get_response_or_404(
    response_id: int,
    db: Session = Depends(get_db)
) -> survey_models.Response:
    """
    Dependency to get response by ID or raise 404

    Args:
        response_id: Response ID
        db: Database session

    Returns:
        Response model instance

    Raises:
        HTTPException: 404 if response not found
    """
    response = survey_crud.get_response(db, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response


# =============================================================================
# COMBINED VALIDATION HELPERS
# =============================================================================

def validate_survey_active(survey: survey_models.Survey) -> survey_models.Survey:
    """
    Validate that survey is active

    Args:
        survey: Survey model instance

    Returns:
        Survey model instance (if valid)

    Raises:
        HTTPException: 400 if survey is not active
    """
    if not survey.is_active:
        raise HTTPException(status_code=400, detail="Survey is not active")
    return survey


def validate_submission_not_completed(submission: survey_models.Submission) -> survey_models.Submission:
    """
    Validate that submission is not yet completed

    Args:
        submission: Submission model instance

    Returns:
        Submission model instance (if valid)

    Raises:
        HTTPException: 400 if submission is already completed
    """
    if submission.is_completed:
        raise HTTPException(status_code=400, detail="Cannot add responses to completed submission")
    return submission
