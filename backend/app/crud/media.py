"""Media CRUD operations using CRUDBase"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List

from app.crud.base import CRUDBase
from app.models.media import Media
from app.schemas.media import MediaCreate, MediaUpdate, MediaGalleryResponse, MediaGalleryItem
from app.utils.json import safe_json_parse, safe_json_dumps


class CRUDMedia(CRUDBase[Media, MediaCreate, MediaUpdate]):
    """CRUD operations for Media model"""

    def get_by_response_id(self, db: Session, response_id: int) -> Optional[Media]:
        """Get media analysis by response ID"""
        return db.query(self.model).filter(self.model.response_id == response_id).first()

    def create_or_update(
        self,
        db: Session,
        *,
        response_id: int,
        description: Optional[str] = None,
        transcript: Optional[str] = None,
        brands: Optional[List[str]] = None,
        reporting_labels: Optional[List[str]] = None
    ) -> Media:
        """Create or update media analysis for a response"""

        # Convert lists to JSON strings if provided using safe utility
        brands_json = safe_json_dumps(brands)
        labels_json = safe_json_dumps(reporting_labels)

        # Check if media analysis already exists
        existing_media = self.get_by_response_id(db, response_id)

        if existing_media:
            # Update existing record
            update_data = {}
            if description is not None:
                update_data['description'] = description
            if transcript is not None:
                update_data['transcript'] = transcript
            if brands_json is not None:
                update_data['brands_detected'] = brands_json
            if labels_json is not None:
                update_data['reporting_labels'] = labels_json

            return self.update(db, db_obj=existing_media, obj_in=update_data)
        else:
            # Create new record
            media_data = MediaCreate(
                response_id=response_id,
                description=description,
                transcript=transcript,
                brands_detected=brands_json,
                reporting_labels=labels_json
            )
            return self.create(db, obj_in=media_data)

    def get_gallery(
        self,
        db: Session,
        survey_slug: str,
        labels: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        genders: Optional[List[str]] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None
    ) -> MediaGalleryResponse:
        """Get media gallery items for a survey with optional filtering"""
        from app.models.survey import Survey, Submission, Response

        # Start with base query joining all necessary tables
        query = db.query(
            self.model,
            Response.photo_url,
            Response.video_url,
            Response.question,
            Response.responded_at,
            Submission.id.label('submission_id'),
            Submission.email,
            Submission.region,
            Submission.gender,
            Submission.age
        ).join(Response, self.model.response_id == Response.id) \
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
            label_conditions = []
            for label in labels:
                label_conditions.append(self.model.reporting_labels.contains(f'"{label}"'))
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
            # Parse JSON fields safely using utility
            brands_list = safe_json_parse(media.brands_detected, [])
            labels_list = safe_json_parse(media.reporting_labels, [])

            # Create items for both photo and video if they exist
            if photo_url:
                items.append(MediaGalleryItem(
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
                items.append(MediaGalleryItem(
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

        return MediaGalleryResponse(
            items=items,
            total_count=len(items),
            photo_count=photo_count,
            video_count=video_count
        )


# Create singleton instance
media = CRUDMedia(Media)


# Backward compatibility - maintain old function signatures
def create_media_analysis(db: Session, media_data: MediaCreate) -> Media:
    """Create a new media analysis record"""
    return media.create(db, obj_in=media_data)


def get_media_by_response_id(db: Session, response_id: int) -> Optional[Media]:
    """Get media analysis by response ID"""
    return media.get_by_response_id(db, response_id)


def update_media_analysis(db: Session, media_id: int, media_update: MediaUpdate) -> Optional[Media]:
    """Update media analysis"""
    return media.update_by_id(db, id=media_id, obj_in=media_update)


def create_or_update_media_analysis(
    db: Session,
    response_id: int,
    description: Optional[str] = None,
    transcript: Optional[str] = None,
    brands: Optional[List[str]] = None,
    reporting_labels: Optional[List[str]] = None
) -> Media:
    """Create or update media analysis for a response"""
    return media.create_or_update(
        db,
        response_id=response_id,
        description=description,
        transcript=transcript,
        brands=brands,
        reporting_labels=reporting_labels
    )


def get_media_analysis(db: Session, media_id: int) -> Optional[Media]:
    """Get media analysis by ID"""
    return media.get(db, media_id)


def get_all_media_analyses(db: Session, skip: int = 0, limit: int = 100) -> List[Media]:
    """Get all media analyses"""
    return media.get_multi(db, skip=skip, limit=limit)


def get_media_gallery(
    db: Session,
    survey_slug: str,
    labels: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    genders: Optional[List[str]] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None
) -> MediaGalleryResponse:
    """Get media gallery items for a survey with optional filtering"""
    return media.get_gallery(
        db,
        survey_slug=survey_slug,
        labels=labels,
        regions=regions,
        genders=genders,
        age_min=age_min,
        age_max=age_max
    )
