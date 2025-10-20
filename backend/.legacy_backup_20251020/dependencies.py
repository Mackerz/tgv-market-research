"""FastAPI dependencies for reusable request handling"""
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import survey_crud
import survey_models


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
