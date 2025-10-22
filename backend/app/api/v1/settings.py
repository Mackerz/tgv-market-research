"""Settings API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.schemas import settings as settings_schemas
from app.crud import settings as settings_crud
from app.crud import survey as survey_crud
from app.dependencies import get_survey_or_404
from app.core.auth import require_admin

router = APIRouter(prefix="/api/reports", tags=["settings"])


# =============================================================================
# SETTINGS ENDPOINTS
# =============================================================================

@router.get("/{survey_slug}/settings")
def get_report_settings(
    survey_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get report settings for a survey (ADMIN ONLY)"""
    # Get survey using dependency helper
    survey = get_survey_or_404(survey_slug, db)

    # Get settings with questions
    settings = settings_crud.get_report_settings_with_questions(db, survey.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings


@router.put("/{survey_slug}/settings/age-ranges")
def update_age_ranges(
    survey_slug: str,
    age_ranges_update: List[settings_schemas.AgeRange],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update age ranges for a survey (ADMIN ONLY)"""
    # Get survey using dependency helper
    survey = get_survey_or_404(survey_slug, db)

    # Update age ranges
    settings_update = settings_schemas.ReportSettingsUpdate(age_ranges=age_ranges_update)
    updated_settings = settings_crud.update_report_settings(db, survey.id, settings_update)

    if not updated_settings:
        # Create settings if they don't exist
        updated_settings = settings_crud.create_or_get_report_settings(db, survey.id)
        updated_settings = settings_crud.update_report_settings(db, survey.id, settings_update)

    return {"message": "Age ranges updated successfully", "age_ranges": updated_settings.age_ranges}


@router.put("/{survey_slug}/settings/question-display-names")
def update_question_display_names(
    survey_slug: str,
    updates: settings_schemas.BulkQuestionDisplayNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Bulk update question display names for a survey (ADMIN ONLY)"""
    # Get survey using dependency helper
    survey = get_survey_or_404(survey_slug, db)

    # Get or create settings
    settings = settings_crud.create_or_get_report_settings(db, survey.id)

    # Update question display names
    success = settings_crud.bulk_update_question_display_names(
        db,
        settings.id,
        updates.question_updates
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to update question display names")

    return {"message": "Question display names updated successfully"}


@router.put("/{survey_slug}/settings/question-display-names/{question_id}")
def update_single_question_display_name(
    survey_slug: str,
    question_id: str,
    display_name_update: settings_schemas.QuestionDisplayNameUpdate,
    db: Session = Depends(get_db)
):
    """Update display name for a single question"""
    # Get survey using dependency helper
    survey = get_survey_or_404(survey_slug, db)

    # Get or create settings
    settings = settings_crud.create_or_get_report_settings(db, survey.id)

    # Update question display name
    updated_question = settings_crud.update_question_display_name(
        db,
        settings.id,
        question_id,
        display_name_update.display_name
    )

    if not updated_question:
        raise HTTPException(status_code=404, detail="Question not found")

    return {
        "message": "Question display name updated successfully",
        "question": {
            "id": updated_question.id,
            "question_id": updated_question.question_id,
            "question_text": updated_question.question_text,
            "display_name": updated_question.display_name,
            "effective_display_name": settings_crud.get_effective_display_name(updated_question)
        }
    }
