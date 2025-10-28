from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Dict, Any
import json

from app.models import settings as settings_models
from app.schemas import settings as settings_schemas
from app.models import survey


def create_or_get_report_settings(db: Session, survey_id: int) -> settings_models.ReportSettings:
    """Create report settings for a survey or return existing ones"""
    # Check if settings already exist
    existing_settings = db.query(settings_models.ReportSettings).filter(
        settings_models.ReportSettings.survey_id == survey_id
    ).first()

    if existing_settings:
        return existing_settings

    # Create new settings with default age ranges
    default_age_ranges = [
        {"min": 0, "max": 18, "label": "0-18"},
        {"min": 18, "max": 25, "label": "18-25"},
        {"min": 25, "max": 40, "label": "25-40"},
        {"min": 40, "max": 60, "label": "40-60"},
        {"min": 60, "max": None, "label": "60+"}
    ]

    db_settings = settings_models.ReportSettings(
        survey_id=survey_id,
        age_ranges=default_age_ranges
    )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)

    # Also create question display names for all questions in the survey
    _sync_question_display_names(db, db_settings)

    return db_settings


def get_report_settings(db: Session, survey_id: int) -> Optional[settings_models.ReportSettings]:
    """Get report settings for a survey"""
    return db.query(settings_models.ReportSettings).filter(
        settings_models.ReportSettings.survey_id == survey_id
    ).first()


def update_report_settings(db: Session, survey_id: int, settings_update: settings_schemas.ReportSettingsUpdate) -> Optional[settings_models.ReportSettings]:
    """Update report settings for a survey"""
    db_settings = db.query(settings_models.ReportSettings).filter(
        settings_models.ReportSettings.survey_id == survey_id
    ).first()

    if not db_settings:
        return None

    update_data = settings_update.model_dump(exclude_unset=True)

    # Convert age_ranges to dict format for JSON storage
    if 'age_ranges' in update_data:
        age_ranges_list = []
        for age_range in update_data['age_ranges']:
            if hasattr(age_range, 'model_dump'):
                age_ranges_list.append(age_range.model_dump())
            else:
                age_ranges_list.append(age_range)
        update_data['age_ranges'] = age_ranges_list

    for field, value in update_data.items():
        setattr(db_settings, field, value)

    db.commit()
    db.refresh(db_settings)
    return db_settings


def _sync_question_display_names(db: Session, report_settings: settings_models.ReportSettings):
    """Synchronize question display names with survey flow"""
    # Get the survey
    survey_obj = db.query(survey.Survey).filter(
        survey.Survey.id == report_settings.survey_id
    ).first()

    if not survey_obj or not survey_obj.survey_flow:
        return

    # Get existing question display names
    existing_questions = {q.question_id: q for q in report_settings.question_display_names}

    # Process each question in the survey flow
    for question_data in survey_obj.survey_flow:
        question_id = question_data.get('id')
        question_text = question_data.get('question', '')

        if not question_id:
            continue

        if question_id in existing_questions:
            # Update existing question if text has changed
            existing_q = existing_questions[question_id]
            if existing_q.question_text != question_text:
                existing_q.question_text = question_text
        else:
            # Create new question display name entry
            new_question_display = settings_models.QuestionDisplayName(
                report_settings_id=report_settings.id,
                question_id=question_id,
                question_text=question_text,
                display_name=None  # Will use original question text if None
            )
            db.add(new_question_display)

    # Remove question display names for questions that no longer exist in survey flow
    survey_question_ids = {q.get('id') for q in survey_obj.survey_flow if q.get('id')}
    for existing_q in list(existing_questions.values()):
        if existing_q.question_id not in survey_question_ids:
            db.delete(existing_q)

    db.commit()


def update_question_display_name(db: Session, report_settings_id: int, question_id: str, display_name: Optional[str]) -> Optional[settings_models.QuestionDisplayName]:
    """Update display name for a specific question"""
    db_question = db.query(settings_models.QuestionDisplayName).filter(
        and_(
            settings_models.QuestionDisplayName.report_settings_id == report_settings_id,
            settings_models.QuestionDisplayName.question_id == question_id
        )
    ).first()

    if not db_question:
        return None

    db_question.display_name = display_name
    db.commit()
    db.refresh(db_question)
    return db_question


def bulk_update_question_display_names(db: Session, report_settings_id: int, question_updates: List[Dict[str, Any]]) -> bool:
    """Bulk update display names for multiple questions"""
    try:
        for update in question_updates:
            question_id = update.get('question_id')
            display_name = update.get('display_name')

            if not question_id:
                continue

            db_question = db.query(settings_models.QuestionDisplayName).filter(
                and_(
                    settings_models.QuestionDisplayName.report_settings_id == report_settings_id,
                    settings_models.QuestionDisplayName.question_id == question_id
                )
            ).first()

            if db_question:
                db_question.display_name = display_name if display_name else None

        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def get_report_settings_with_questions(db: Session, survey_id: int) -> Optional[Dict[str, Any]]:
    """Get report settings along with available questions from survey flow"""
    # Get or create settings
    settings = create_or_get_report_settings(db, survey_id)

    # Get survey to extract questions
    survey_obj = db.query(survey.Survey).filter(
        survey.Survey.id == survey_id
    ).first()

    if not survey_obj:
        return None

    # Extract available questions from survey flow
    available_questions = []
    if survey_obj.survey_flow:
        for question_data in survey_obj.survey_flow:
            if question_data.get('id') and question_data.get('question'):
                available_questions.append({
                    'id': question_data['id'],
                    'question': question_data['question'],
                    'question_type': question_data.get('question_type', 'unknown')
                })

    # Build response
    return {
        'id': settings.id,
        'survey_id': settings.survey_id,
        'age_ranges': settings.age_ranges,
        'created_at': settings.created_at,
        'updated_at': settings.updated_at,
        'question_display_names': settings.question_display_names,
        'available_questions': available_questions
    }


def get_effective_display_name(question_display_name: settings_models.QuestionDisplayName) -> str:
    """Get the effective display name - returns custom name if set, otherwise original question text"""
    return question_display_name.display_name if question_display_name.display_name else question_display_name.question_text