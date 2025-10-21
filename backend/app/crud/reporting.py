from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import json

from app.models import survey
from app.models import media
from app.crud import settings as settings_crud
from app.schemas import reporting as reporting_schemas
from app.utils.queries import get_approved_submissions_query, get_approved_submission_ids_subquery
from app.utils.charts import ChartColorPalette
from app.utils.json import safe_json_parse


def categorize_age(age: Optional[int], age_ranges: List[Dict]) -> Optional[str]:
    """Categorize age into appropriate age range"""
    if age is None:
        return None

    for range_config in age_ranges:
        min_age = range_config['min']
        max_age = range_config.get('max')  # Can be None

        if max_age is None:  # No upper limit (e.g., "60+")
            if age >= min_age:
                return range_config['label']
        else:
            if min_age <= age < max_age:
                return range_config['label']

    return "Unknown"


def get_demographic_data(db: Session, survey_id: int, age_ranges: List[Dict]) -> reporting_schemas.DemographicData:
    """Get demographic breakdown for completed and approved submissions"""

    # Get completed and approved submissions using reusable query helper
    submissions = get_approved_submissions_query(db, survey_id).all()

    # Age range analysis
    age_counts = defaultdict(int)
    for submission in submissions:
        age_category = categorize_age(submission.age, age_ranges)
        if age_category:
            age_counts[age_category] += 1

    # Ensure all age ranges are represented (even with 0 count)
    for range_config in age_ranges:
        if range_config['label'] not in age_counts:
            age_counts[range_config['label']] = 0

    # Region analysis
    region_counts = Counter(submission.region for submission in submissions)

    # Gender analysis
    gender_counts = Counter(submission.gender for submission in submissions)

    return reporting_schemas.DemographicData(
        age_ranges=reporting_schemas.ChartData(
            labels=list(age_counts.keys()),
            data=list(age_counts.values()),
            backgroundColor=ChartColorPalette.get_colors(len(age_counts))
        ),
        regions=reporting_schemas.ChartData(
            labels=list(region_counts.keys()),
            data=list(region_counts.values()),
            backgroundColor=ChartColorPalette.get_colors(len(region_counts))
        ),
        genders=reporting_schemas.ChartData(
            labels=list(gender_counts.keys()),
            data=list(gender_counts.values()),
            backgroundColor=ChartColorPalette.get_gender_colors(len(gender_counts))
        )
    )


def get_question_response_data(
    db: Session,
    survey_id: int,
    survey_flow: List[Dict],
    question_display_names: Dict[str, str]
) -> List[reporting_schemas.QuestionResponseData]:
    """Get response data for all single and multi-choice questions"""

    response_data = []

    # Get all completed and approved submission IDs using reusable helper
    approved_submission_ids = get_approved_submission_ids_subquery(db, survey_id)

    for question in survey_flow:
        question_id = question.get('id')
        question_text = question.get('question', '')
        question_type = question.get('question_type', '')

        # Only process single and multi-choice questions
        if question_type not in ['single', 'multi']:
            continue

        # Get display name if available
        display_name = question_display_names.get(question_id)
        effective_display_name = display_name if display_name else question_text

        if question_type == 'single':
            # Single choice: count submissions per answer
            responses = db.query(survey.Response).filter(
                and_(
                    survey.Response.submission_id.in_(approved_submission_ids),
                    survey.Response.question == question_text,
                    survey.Response.question_type == 'single',
                    survey.Response.single_answer.isnot(None)
                )
            ).all()

            answer_counts = Counter(response.single_answer for response in responses)

        elif question_type == 'multi':
            # Multi-choice: count distinct submissions per answer option
            responses = db.query(survey.Response).filter(
                and_(
                    survey.Response.submission_id.in_(approved_submission_ids),
                    survey.Response.question == question_text,
                    survey.Response.question_type == 'multi',
                    survey.Response.multiple_choice_answer.isnot(None)
                )
            ).all()

            # Count submissions that selected each option
            answer_counts = defaultdict(int)
            for response in responses:
                if response.multiple_choice_answer:
                    for answer in response.multiple_choice_answer:
                        answer_counts[answer] += 1

        # Create chart data if we have responses
        if answer_counts:
            chart_data = reporting_schemas.ChartData(
                labels=list(answer_counts.keys()),
                data=list(answer_counts.values()),
                backgroundColor=ChartColorPalette.get_colors(len(answer_counts))
            )

            response_data.append(reporting_schemas.QuestionResponseData(
                question_id=question_id,
                question_text=question_text,
                display_name=effective_display_name,
                question_type=question_type,
                chart_data=chart_data
            ))

    return response_data


def get_media_analysis_data(db: Session, survey_id: int) -> reporting_schemas.MediaData:
    """Get media analysis data for photos and videos"""

    # Get all completed and approved submission IDs using reusable helper
    approved_submission_ids = get_approved_submission_ids_subquery(db, survey_id)

    # Get photo responses with media analysis
    photo_responses = db.query(survey.Response, media.Media).join(
        media.Media, survey.Response.id == media.Media.response_id
    ).filter(
        and_(
            survey.Response.submission_id.in_(approved_submission_ids),
            survey.Response.question_type == 'photo',
            survey.Response.photo_url.isnot(None),
            media.Media.reporting_labels.isnot(None)
        )
    ).all()

    # Get video responses with media analysis
    video_responses = db.query(survey.Response, media.Media).join(
        media.Media, survey.Response.id == media.Media.response_id
    ).filter(
        and_(
            survey.Response.submission_id.in_(approved_submission_ids),
            survey.Response.question_type == 'video',
            survey.Response.video_url.isnot(None),
            media.Media.reporting_labels.isnot(None)
        )
    ).all()

    # Process photo reporting labels using safe JSON parser
    photo_label_counts = defaultdict(set)  # Use set to track distinct submission IDs
    for response, media_obj in photo_responses:
        labels = safe_json_parse(media_obj.reporting_labels, [])
        for label in labels:
            photo_label_counts[label].add(response.submission_id)

    # Process video reporting labels using safe JSON parser
    video_label_counts = defaultdict(set)  # Use set to track distinct submission IDs
    for response, media_obj in video_responses:
        labels = safe_json_parse(media_obj.reporting_labels, [])
        for label in labels:
            video_label_counts[label].add(response.submission_id)

    # Convert sets to counts
    photo_final_counts = {label: len(submission_ids) for label, submission_ids in photo_label_counts.items()}
    video_final_counts = {label: len(submission_ids) for label, submission_ids in video_label_counts.items()}

    return reporting_schemas.MediaData(
        photos=reporting_schemas.ChartData(
            labels=list(photo_final_counts.keys()),
            data=list(photo_final_counts.values()),
            backgroundColor=ChartColorPalette.get_colors(len(photo_final_counts))
        ),
        videos=reporting_schemas.ChartData(
            labels=list(video_final_counts.keys()),
            data=list(video_final_counts.values()),
            backgroundColor=ChartColorPalette.get_colors(len(video_final_counts))
        )
    )


def get_reporting_data(db: Session, survey_slug: str) -> Optional[reporting_schemas.ReportingData]:
    """Get comprehensive reporting data for a survey"""

    # Get survey
    survey_obj = db.query(survey.Survey).filter(
        survey.Survey.survey_slug == survey_slug
    ).first()

    if not survey_obj:
        return None

    # Get total submission count
    total_submissions = db.query(survey.Submission).filter(
        survey.Submission.survey_id == survey_obj.id
    ).count()

    # Get completed and approved submission count
    completed_approved_count = db.query(survey.Submission).filter(
        and_(
            survey.Submission.survey_id == survey_obj.id,
            survey.Submission.is_completed == True,
            survey.Submission.is_approved == True
        )
    ).count()

    # Get or create report settings to get age ranges and question display names
    settings = settings_crud.create_or_get_report_settings(db, survey_obj.id)

    # Build question display name mapping
    question_display_names = {}
    for q in settings.question_display_names:
        if q.display_name:
            question_display_names[q.question_id] = q.display_name

    # Get demographic data
    demographics = get_demographic_data(db, survey_obj.id, settings.age_ranges)

    # Get question response data
    question_responses = get_question_response_data(
        db,
        survey_obj.id,
        survey_obj.survey_flow,
        question_display_names
    )

    # Get media analysis data
    media_analysis = get_media_analysis_data(db, survey_obj.id)

    return reporting_schemas.ReportingData(
        total_submissions=total_submissions,
        completed_approved_submissions=completed_approved_count,
        survey_name=survey_obj.name,
        survey_slug=survey_obj.survey_slug,
        generated_at=datetime.now(),
        demographics=demographics,
        question_responses=question_responses,
        media_analysis=media_analysis
    )