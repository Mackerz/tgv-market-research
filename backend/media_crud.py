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