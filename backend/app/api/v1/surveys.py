"""Survey API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.models import survey as survey_models
from app.schemas import survey as survey_schemas
from app.crud import survey as survey_crud
from app.integrations.gcp.storage import upload_survey_photo, upload_survey_video
from app.dependencies import get_survey_or_404, get_survey_by_id_or_404
from app.core.rate_limits import get_rate_limit
from app.core.auth import RequireAPIKey
from app.utils.validation import FileValidator

router = APIRouter(prefix="/api", tags=["surveys"])
limiter = Limiter(key_func=get_remote_address)


# =============================================================================
# SURVEY MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/surveys/", response_model=survey_schemas.Survey)
@limiter.limit(get_rate_limit("survey_create"))
def create_survey(
    request: Request,
    survey: survey_schemas.SurveyCreate,
    db: Session = Depends(get_db),
    api_key: str = RequireAPIKey
):
    """
    Create a new survey (ADMIN ONLY)

    Rate limit: 10/minute to prevent spam
    Requires: X-API-Key header
    """
    try:
        return survey_crud.create_survey(db=db, survey_data=survey)
    except Exception as e:
        # Handle duplicate slug error
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise


@router.get("/surveys/")
def read_surveys(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    search: Optional[str] = None,
    client: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    """Get all surveys with optional search, filtering, and sorting"""
    query = db.query(survey_models.Survey)

    # Filter by active status
    if active_only:
        query = query.filter(survey_models.Survey.is_active == True)

    # Search by survey name
    if search:
        from app.utils.sql_helpers import escape_like_pattern
        escaped_search = escape_like_pattern(search)
        query = query.filter(survey_models.Survey.name.ilike(f"%{escaped_search}%", escape='\\'))

    # Filter by client
    if client:
        from app.utils.sql_helpers import escape_like_pattern
        escaped_client = escape_like_pattern(client)
        query = query.filter(survey_models.Survey.client.ilike(f"%{escaped_client}%", escape='\\'))

    # Sorting
    if sort_by == "created_at":
        order_column = survey_models.Survey.created_at
    elif sort_by == "name":
        order_column = survey_models.Survey.name
    elif sort_by == "client":
        order_column = survey_models.Survey.client
    else:
        order_column = survey_models.Survey.created_at

    if sort_order == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(order_column)

    # Get total count before pagination
    total_count = query.count()

    # Paginate
    surveys = query.offset(skip).limit(limit).all()

    return {
        "surveys": surveys,
        "total_count": total_count
    }


@router.get("/surveys/{survey_id}", response_model=survey_schemas.SurveyWithSubmissions)
def read_survey(survey_id: int, db: Session = Depends(get_db)):
    """Get a specific survey by ID"""
    # Get survey using dependency helper
    return get_survey_by_id_or_404(survey_id, db)


@router.get("/surveys/slug/{survey_slug}", response_model=survey_schemas.Survey)
def read_survey_by_slug(survey_slug: str, db: Session = Depends(get_db)):
    """Get a specific survey by slug"""
    # Get survey using dependency helper
    return get_survey_or_404(survey_slug, db)


@router.put("/surveys/{survey_id}", response_model=survey_schemas.Survey)
def update_survey(
    survey_id: int,
    survey: survey_schemas.SurveyUpdate,
    db: Session = Depends(get_db),
    api_key: str = RequireAPIKey
):
    """Update a survey (ADMIN ONLY - Requires: X-API-Key header)"""
    db_survey = survey_crud.update_survey(db=db, survey_id=survey_id, survey_data=survey)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey


@router.patch("/surveys/{survey_id}/toggle-status", response_model=survey_schemas.Survey)
def toggle_survey_status(
    survey_id: int,
    db: Session = Depends(get_db),
    api_key: str = RequireAPIKey
):
    """
    Toggle survey active status (ADMIN ONLY - Requires: X-API-Key header)

    This is a convenience endpoint that toggles the is_active field.
    Returns the updated survey with the new status.
    """
    # Get current survey
    db_survey = get_survey_by_id_or_404(survey_id, db)

    # Toggle is_active
    updated_survey = survey_crud.update_survey(
        db=db,
        survey_id=survey_id,
        survey_data=survey_schemas.SurveyUpdate(is_active=not db_survey.is_active)
    )

    if updated_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    return updated_survey


@router.delete("/surveys/{survey_id}")
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    api_key: str = RequireAPIKey
):
    """Delete a survey (ADMIN ONLY - Requires: X-API-Key header)"""
    success = survey_crud.delete_survey(db=db, survey_id=survey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Survey deleted successfully"}


# =============================================================================
# FILE UPLOAD ENDPOINTS
# =============================================================================

@router.post("/surveys/{survey_slug}/upload/photo", response_model=survey_schemas.FileUploadResponse)
@limiter.limit(get_rate_limit("file_upload"))
async def upload_photo(request: Request, survey_slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a photo for a survey (Rate limit: 20/minute for cost control)"""
    # Verify survey exists using dependency helper
    get_survey_or_404(survey_slug, db)

    # Validate file upload (size, MIME type, content)
    file = await FileValidator.validate_image(file)

    try:
        file_url, file_id = upload_survey_photo(file, survey_slug)
        return survey_schemas.FileUploadResponse(
            file_url=file_url,
            file_id=file_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Photo upload failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="File upload failed")


@router.post("/surveys/{survey_slug}/upload/video", response_model=survey_schemas.FileUploadResponse)
@limiter.limit(get_rate_limit("file_upload"))
async def upload_video(request: Request, survey_slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a video for a survey (Rate limit: 20/minute for cost control)"""
    # Verify survey exists using dependency helper
    get_survey_or_404(survey_slug, db)

    # Validate file upload (size, MIME type, content)
    file = await FileValidator.validate_video(file)

    try:
        file_url, file_id, thumbnail_url = upload_survey_video(file, survey_slug)
        return survey_schemas.FileUploadResponse(
            file_url=file_url,
            file_id=file_id,
            thumbnail_url=thumbnail_url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Video upload failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="File upload failed")
