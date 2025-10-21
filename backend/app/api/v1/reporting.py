"""Reporting API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_
from typing import Optional

from app.core.database import get_db
from app.models import survey as survey_models
from app.schemas import survey as survey_schemas
from app.schemas import reporting as reporting_schemas
from app.schemas import media as media_schemas
from app.crud import survey as survey_crud
from app.crud import reporting as reporting_crud
from app.crud import media as media_crud
from app.dependencies import get_survey_or_404, get_submission_for_survey_or_404
from app.utils.queries import get_submission_counts
from app.core.auth import RequireAPIKey

router = APIRouter(prefix="/api/reports", tags=["reporting"])


# =============================================================================
# REPORTING ENDPOINTS
# =============================================================================

@router.get("/{survey_slug}/submissions")
def get_report_submissions(
    survey_slug: str,
    approved: Optional[str] = None,
    sort_by: str = "submitted_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get submissions for reporting with filtering and sorting"""

    # Get survey using dependency helper
    survey = get_survey_or_404(survey_slug, db)

    # Build query - only include completed submissions
    # Use selectinload to prevent N+1 queries when accessing responses
    query = db.query(survey_models.Submission).options(
        selectinload(survey_models.Submission.responses)
    ).filter(
        survey_models.Submission.survey_id == survey.id,
        survey_models.Submission.is_completed == True
    )

    # Apply approved filter
    # approved can be: None (all), "true" (approved), "false" (rejected), "null" (pending)
    if approved is not None:
        if approved.lower() == "null":
            query = query.filter(survey_models.Submission.is_approved.is_(None))
        elif approved.lower() == "true":
            query = query.filter(survey_models.Submission.is_approved == True)
        elif approved.lower() == "false":
            query = query.filter(survey_models.Submission.is_approved == False)

    # Apply sorting
    sort_column = getattr(survey_models.Submission, sort_by, None)
    if sort_column is None:
        sort_column = survey_models.Submission.submitted_at

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Apply pagination
    submissions = query.offset(skip).limit(limit).all()

    # Get counts using helper (eliminates duplicate query logic)
    counts = get_submission_counts(db, survey.id)

    return {
        "submissions": submissions,
        "total_count": counts['completed'],  # Only completed for reporting
        "approved_count": counts['approved'],
        "rejected_count": counts['rejected'],
        "pending_count": counts['pending'],
        "survey": survey
    }


@router.get("/{survey_slug}/submissions/{submission_id}")
def get_report_submission_detail(
    survey_slug: str,
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed submission with responses and media analysis for reporting"""
    # Get survey and submission using dependency helper
    survey, submission = get_submission_for_survey_or_404(survey_slug, submission_id, db)

    # Get responses with media analysis
    responses = survey_crud.get_responses_by_submission(db, submission_id)

    # Enrich responses with media analysis
    enriched_responses = []
    for response in responses:
        response_data = {
            "id": response.id,
            "question": response.question,
            "question_type": response.question_type,
            "single_answer": response.single_answer,
            "free_text_answer": response.free_text_answer,
            "multiple_choice_answer": response.multiple_choice_answer,
            "photo_url": response.photo_url,
            "video_url": response.video_url,
            "video_thumbnail_url": response.video_thumbnail_url,
            "responded_at": response.responded_at,
            "media_analysis": None
        }

        # Get media analysis if it exists
        if response.media_analysis:
            from app.utils.json import safe_json_parse

            for media in response.media_analysis:
                # Parse JSON strings safely
                brands_list = safe_json_parse(media.brands_detected, [])
                labels_list = safe_json_parse(media.reporting_labels, [])

                response_data["media_analysis"] = {
                    "id": media.id,
                    "description": media.description,
                    "transcript": media.transcript,
                    "brands_detected": brands_list,
                    "reporting_labels": labels_list
                }

        enriched_responses.append(response_data)

    return {
        "submission": submission,
        "responses": enriched_responses,
        "survey": survey
    }


@router.put("/{survey_slug}/submissions/{submission_id}/approve")
def approve_submission(
    survey_slug: str,
    submission_id: int,
    db: Session = Depends(get_db),
    api_key: str = RequireAPIKey
):
    """Approve a submission (ADMIN ONLY - Requires: X-API-Key header)"""
    # Get survey and submission using dependency helper
    survey, submission = get_submission_for_survey_or_404(survey_slug, submission_id, db)

    # Update submission
    submission = survey_crud.update_submission(
        db,
        submission_id,
        survey_schemas.SubmissionUpdate(is_approved=True)
    )

    return {"message": "Submission approved", "submission": submission}


@router.put("/{survey_slug}/submissions/{submission_id}/reject")
def reject_submission(
    survey_slug: str,
    submission_id: int,
    db: Session = Depends(get_db),
    api_key: str = RequireAPIKey
):
    """Reject a submission (ADMIN ONLY - Requires: X-API-Key header)"""
    # Get survey and submission using dependency helper
    survey, submission = get_submission_for_survey_or_404(survey_slug, submission_id, db)

    # Update submission
    submission = survey_crud.update_submission(
        db,
        submission_id,
        survey_schemas.SubmissionUpdate(is_approved=False)
    )

    return {"message": "Submission rejected", "submission": submission}


@router.get("/{survey_slug}/data", response_model=reporting_schemas.ReportingData)
def get_reporting_data(survey_slug: str, db: Session = Depends(get_db)):
    """Get comprehensive reporting data including demographics and question responses"""
    reporting_data = reporting_crud.get_reporting_data(db, survey_slug)

    if not reporting_data:
        raise HTTPException(status_code=404, detail="Survey not found")

    return reporting_data


@router.get("/{survey_slug}/media-gallery", response_model=media_schemas.MediaGalleryResponse)
def get_media_gallery(
    survey_slug: str,
    labels: Optional[str] = None,
    regions: Optional[str] = None,
    genders: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get media gallery for a survey with optional filtering"""
    # Parse comma-separated filter parameters
    labels_list = labels.split(',') if labels else None
    regions_list = regions.split(',') if regions else None
    genders_list = genders.split(',') if genders else None

    try:
        gallery_data = media_crud.get_media_gallery(
            db=db,
            survey_slug=survey_slug,
            labels=labels_list,
            regions=regions_list,
            genders=genders_list,
            age_min=age_min,
            age_max=age_max
        )
        return gallery_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch media gallery: {str(e)}")
