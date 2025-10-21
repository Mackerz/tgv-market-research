"""Survey API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.core.database import get_db
from app.models import survey as survey_models
from app.schemas import survey as survey_schemas
from app.crud import survey as survey_crud
from app.integrations.gcp.storage import upload_survey_photo, upload_survey_video
from app.dependencies import get_survey_or_404, get_survey_by_id_or_404

router = APIRouter(prefix="/api", tags=["surveys"])


# =============================================================================
# SURVEY MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/surveys/", response_model=survey_schemas.Survey)
def create_survey(survey: survey_schemas.SurveyCreate, db: Session = Depends(get_db)):
    """Create a new survey"""
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
        query = query.filter(survey_models.Survey.name.ilike(f"%{search}%"))

    # Filter by client
    if client:
        query = query.filter(survey_models.Survey.client.ilike(f"%{client}%"))

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
def update_survey(survey_id: int, survey: survey_schemas.SurveyUpdate, db: Session = Depends(get_db)):
    """Update a survey"""
    db_survey = survey_crud.update_survey(db=db, survey_id=survey_id, survey_data=survey)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey


@router.delete("/surveys/{survey_id}")
def delete_survey(survey_id: int, db: Session = Depends(get_db)):
    """Delete a survey"""
    success = survey_crud.delete_survey(db=db, survey_id=survey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Survey deleted successfully"}


# =============================================================================
# FILE UPLOAD ENDPOINTS
# =============================================================================

@router.post("/surveys/{survey_slug}/upload/photo", response_model=survey_schemas.FileUploadResponse)
async def upload_photo(survey_slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a photo for a survey"""
    # Verify survey exists using dependency helper
    get_survey_or_404(survey_slug, db)

    try:
        file_url, file_id = upload_survey_photo(file, survey_slug)
        return survey_schemas.FileUploadResponse(
            file_url=file_url,
            file_id=file_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="File upload failed")


@router.post("/surveys/{survey_slug}/upload/video", response_model=survey_schemas.FileUploadResponse)
async def upload_video(survey_slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a video for a survey"""
    # Verify survey exists using dependency helper
    get_survey_or_404(survey_slug, db)

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
        raise HTTPException(status_code=500, detail="File upload failed")
