from sqlalchemy.orm import Session
from typing import Optional, List
import json
import media_models
import media_schemas

def create_media_analysis(db: Session, media: media_schemas.MediaCreate) -> media_models.Media:
    """Create a new media analysis record"""
    db_media = media_models.Media(**media.dict())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def get_media_by_response_id(db: Session, response_id: int) -> Optional[media_models.Media]:
    """Get media analysis by response ID"""
    return db.query(media_models.Media).filter(media_models.Media.response_id == response_id).first()

def update_media_analysis(db: Session, media_id: int, media_update: media_schemas.MediaUpdate) -> Optional[media_models.Media]:
    """Update media analysis"""
    db_media = db.query(media_models.Media).filter(media_models.Media.id == media_id).first()
    if db_media:
        update_data = media_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_media, field, value)
        db.commit()
        db.refresh(db_media)
    return db_media

def create_or_update_media_analysis(
    db: Session,
    response_id: int,
    description: Optional[str] = None,
    transcript: Optional[str] = None,
    brands: Optional[List[str]] = None,
    reporting_labels: Optional[List[str]] = None
) -> media_models.Media:
    """Create or update media analysis for a response"""

    # Convert lists to JSON strings if provided
    brands_json = json.dumps(brands) if brands else None
    labels_json = json.dumps(reporting_labels) if reporting_labels else None

    # Check if media analysis already exists
    existing_media = get_media_by_response_id(db, response_id)

    if existing_media:
        # Update existing record
        update_data = media_schemas.MediaUpdate()
        if description is not None:
            update_data.description = description
        if transcript is not None:
            update_data.transcript = transcript
        if brands_json is not None:
            update_data.brands_detected = brands_json
        if labels_json is not None:
            update_data.reporting_labels = labels_json

        return update_media_analysis(db, existing_media.id, update_data)
    else:
        # Create new record
        media_data = media_schemas.MediaCreate(
            response_id=response_id,
            description=description,
            transcript=transcript,
            brands_detected=brands_json,
            reporting_labels=labels_json
        )
        return create_media_analysis(db, media_data)

def get_media_analysis(db: Session, media_id: int) -> Optional[media_models.Media]:
    """Get media analysis by ID"""
    return db.query(media_models.Media).filter(media_models.Media.id == media_id).first()

def get_all_media_analyses(db: Session, skip: int = 0, limit: int = 100) -> List[media_models.Media]:
    """Get all media analyses"""
    return db.query(media_models.Media).offset(skip).limit(limit).all()

def get_media_gallery(db: Session, survey_slug: str, labels: Optional[List[str]] = None, regions: Optional[List[str]] = None, genders: Optional[List[str]] = None, age_min: Optional[int] = None, age_max: Optional[int] = None) -> media_schemas.MediaGalleryResponse:
    """Get media gallery items for a survey with optional filtering"""
    from survey_models import Survey, Submission, Response

    # Start with base query joining all necessary tables
    query = db.query(
        media_models.Media,
        Response.photo_url,
        Response.video_url,
        Response.question,
        Response.responded_at,
        Submission.id.label('submission_id'),
        Submission.email,
        Submission.region,
        Submission.gender,
        Submission.age
    ).join(Response, media_models.Media.response_id == Response.id) \
     .join(Submission, Response.submission_id == Submission.id) \
     .join(Survey, Submission.survey_id == Survey.id) \
     .filter(Survey.survey_slug == survey_slug) \
     .filter(Submission.is_approved == True) \
     .filter(
         (Response.photo_url.isnot(None)) | (Response.video_url.isnot(None))
     )

    # Apply filters
    if labels:
        # Filter by reporting labels (check if any of the provided labels exist in the JSON)
        from sqlalchemy import or_
        label_conditions = []
        for label in labels:
            label_conditions.append(media_models.Media.reporting_labels.contains(f'"{label}"'))
        query = query.filter(or_(*label_conditions))

    if regions:
        query = query.filter(Submission.region.in_(regions))

    if genders:
        query = query.filter(Submission.gender.in_(genders))

    if age_min is not None:
        query = query.filter(Submission.age >= age_min)

    if age_max is not None:
        query = query.filter(Submission.age <= age_max)

    # Order by most recent first
    query = query.order_by(Response.responded_at.desc())

    results = query.all()

    # Process results into MediaGalleryItem objects
    items = []
    photo_count = 0
    video_count = 0

    for media, photo_url, video_url, question, responded_at, submission_id, email, region, gender, age in results:
        # Parse JSON fields safely
        brands_list = []
        labels_list = []

        if media.brands_detected:
            try:
                brands_list = json.loads(media.brands_detected)
            except:
                pass

        if media.reporting_labels:
            try:
                labels_list = json.loads(media.reporting_labels)
            except:
                pass

        # Create items for both photo and video if they exist
        if photo_url:
            items.append(media_schemas.MediaGalleryItem(
                id=media.id,
                media_type='photo',
                media_url=photo_url,
                thumbnail_url=None,  # Photos don't need thumbnails
                description=media.description,
                transcript=media.transcript,
                brands_detected=brands_list,
                reporting_labels=labels_list,
                submission_id=submission_id,
                submission_email=email,
                submission_region=region,
                submission_gender=gender,
                submission_age=age,
                question=question,
                responded_at=responded_at
            ))
            photo_count += 1

        if video_url:
            items.append(media_schemas.MediaGalleryItem(
                id=media.id,
                media_type='video',
                media_url=video_url,
                thumbnail_url=None,  # Could add thumbnail generation later
                description=media.description,
                transcript=media.transcript,
                brands_detected=brands_list,
                reporting_labels=labels_list,
                submission_id=submission_id,
                submission_email=email,
                submission_region=region,
                submission_gender=gender,
                submission_age=age,
                question=question,
                responded_at=responded_at
            ))
            video_count += 1

    return media_schemas.MediaGalleryResponse(
        items=items,
        total_count=len(items),
        photo_count=photo_count,
        video_count=video_count
    )