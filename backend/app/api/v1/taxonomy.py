import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.taxonomy import get_reporting_label_crud
from app.integrations.gcp.gemini import gemini_labeler
from app.models.media import Media
from app.models.survey import Response, Submission, Survey
from app.schemas.taxonomy import (
    AddSystemLabelRequest,
    GenerateTaxonomyRequest,
    MediaPreview,
    RemoveSystemLabelRequest,
    ReportingLabel,
    ReportingLabelCreate,
    ReportingLabelUpdate,
    TaxonomyOverview,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["taxonomy"])


@router.get("/surveys/{survey_id}/taxonomy", response_model=TaxonomyOverview)
def get_survey_taxonomy(survey_id: int, db: Session = Depends(get_db)):
    """
    Get complete taxonomy overview for a survey including:
    - All reporting labels with their system label mappings
    - Unmapped system labels
    - Total media items count
    """
    # Verify survey exists
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    crud = get_reporting_label_crud(db)

    # Get reporting labels
    reporting_labels = crud.get_by_survey(survey_id)

    # Get unmapped system labels
    unmapped_labels = crud.get_unmapped_system_labels(survey_id)

    # Count total media items
    total_media = (
        db.query(Media)
        .join(Response)
        .join(Submission)
        .filter(Submission.survey_id == survey_id)
        .count()
    )

    return TaxonomyOverview(
        reporting_labels=reporting_labels,
        unmapped_system_labels=unmapped_labels,
        total_media_items=total_media,
    )


@router.post("/surveys/{survey_id}/taxonomy/generate", response_model=list[ReportingLabel])
def generate_taxonomy(
    survey_id: int,
    request: GenerateTaxonomyRequest,
    db: Session = Depends(get_db),
):
    """
    Generate high-level taxonomy categories using Gemini AI based on all
    system labels in the survey. This will create reporting labels and
    automatically map system labels to them.
    """
    # Verify survey exists
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Get all system labels from media in this survey
    media_items = (
        db.query(Media)
        .join(Response)
        .join(Submission)
        .filter(Submission.survey_id == survey_id)
        .all()
    )

    all_labels = []
    for media in media_items:
        if media.reporting_labels:
            try:
                labels = json.loads(media.reporting_labels)
                all_labels.extend(labels)
            except json.JSONDecodeError:
                continue

    if not all_labels:
        raise HTTPException(
            status_code=400,
            detail="No system labels found in this survey. Ensure media has been analyzed first.",
        )

    # Generate taxonomy using Gemini
    logger.info(f"Generating taxonomy for survey {survey_id} with {len(set(all_labels))} unique labels")
    taxonomy_result = gemini_labeler.generate_taxonomy_categories(
        all_labels, max_categories=request.max_categories
    )

    if not taxonomy_result.get("categories"):
        raise HTTPException(
            status_code=500,
            detail="Failed to generate taxonomy. Please try again.",
        )

    # Delete existing reporting labels for this survey
    crud = get_reporting_label_crud(db)
    existing_labels = crud.get_by_survey(survey_id)
    for label in existing_labels:
        db.delete(label)
    db.commit()

    # Create new reporting labels from generated categories
    created_labels = []
    for category in taxonomy_result["categories"]:
        label_create = ReportingLabelCreate(
            survey_id=survey_id,
            label_name=category["category_name"],
            description=category.get("description"),
            is_ai_generated=True,
            system_labels=category.get("system_labels", []),
        )
        created_label = crud.create(label_create)
        created_labels.append(created_label)

    logger.info(f"Created {len(created_labels)} reporting labels for survey {survey_id}")
    return created_labels


@router.post("/reporting-labels", response_model=ReportingLabel, status_code=status.HTTP_201_CREATED)
def create_reporting_label(
    label_data: ReportingLabelCreate,
    db: Session = Depends(get_db),
):
    """Create a new reporting label"""
    # Verify survey exists
    survey = db.query(Survey).filter(Survey.id == label_data.survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    crud = get_reporting_label_crud(db)
    return crud.create(label_data)


@router.put("/reporting-labels/{label_id}", response_model=ReportingLabel)
def update_reporting_label(
    label_id: int,
    label_data: ReportingLabelUpdate,
    db: Session = Depends(get_db),
):
    """Update a reporting label name or description"""
    crud = get_reporting_label_crud(db)
    updated_label = crud.update(label_id, label_data)

    if not updated_label:
        raise HTTPException(status_code=404, detail="Reporting label not found")

    return updated_label


@router.delete("/reporting-labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reporting_label(label_id: int, db: Session = Depends(get_db)):
    """
    Delete a reporting label. Only allowed if no system labels are mapped to it.
    """
    crud = get_reporting_label_crud(db)
    success = crud.delete(label_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete reporting label. Remove all system label mappings first.",
        )


@router.post("/reporting-labels/{label_id}/system-labels", response_model=ReportingLabel)
def add_system_label_to_reporting_label(
    label_id: int,
    request: AddSystemLabelRequest,
    db: Session = Depends(get_db),
):
    """
    Add a system label to a reporting label. If the system label is already
    mapped to another reporting label, it will be moved to this one.
    """
    crud = get_reporting_label_crud(db)
    success = crud.add_system_label(label_id, request.system_label)

    if not success:
        raise HTTPException(status_code=404, detail="Reporting label not found")

    return crud.get(label_id)


@router.delete("/reporting-labels/{label_id}/system-labels", response_model=ReportingLabel)
def remove_system_label_from_reporting_label(
    label_id: int,
    request: RemoveSystemLabelRequest,
    db: Session = Depends(get_db),
):
    """Remove a system label from a reporting label"""
    crud = get_reporting_label_crud(db)
    success = crud.remove_system_label(label_id, request.system_label)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="System label mapping not found",
        )

    return crud.get(label_id)


@router.get("/surveys/{survey_id}/system-labels/{system_label}/media", response_model=list[MediaPreview])
def get_media_by_system_label(
    survey_id: int,
    system_label: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Get sample media items that have a specific system label for preview purposes
    """
    # Verify survey exists
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    crud = get_reporting_label_crud(db)
    media_items = crud.get_media_by_system_label(survey_id, system_label, limit)

    # Convert to MediaPreview format
    previews = []
    for media in media_items:
        response_obj = media.response
        submission = response_obj.submission if response_obj else None

        # Determine media type and URLs
        media_type = "photo" if response_obj.photo_url else "video"
        media_url = response_obj.photo_url or response_obj.video_url or ""
        thumbnail_url = response_obj.video_thumbnail_url if media_type == "video" else None

        respondent_info = {}
        if submission:
            respondent_info = {
                "region": submission.region,
                "gender": submission.gender,
                "age": submission.age,
            }

        previews.append(
            MediaPreview(
                id=media.id,
                media_type=media_type,
                media_url=media_url,
                thumbnail_url=thumbnail_url,
                description=media.description or "",
                submission_id=submission.id if submission else 0,
                respondent_info=respondent_info,
            )
        )

    return previews
