from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging
from database import get_db, engine, Base
import models
import schemas
import crud

# Import survey-related modules
import survey_models
import survey_schemas
import survey_crud
from gcp_storage import upload_survey_photo, upload_survey_video

# Import AI analysis modules
import media_models
import media_schemas
import media_crud
from gcp_ai_analysis import analyze_photo_response, analyze_video_response
from gemini_labeling import generate_labels_for_media, get_survey_label_summary
from fastapi import BackgroundTasks

# Import settings modules
import settings_models
import settings_schemas
import settings_crud

# Import reporting modules
import reporting_schemas
import reporting_crud

# Import models to ensure they're registered
from models import User, Post
from survey_models import Survey, Submission, Response
from media_models import Media
from settings_models import ReportSettings, QuestionDisplayName

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Backend", version="1.0.0")

# Log startup
logger.info("🚀 FastAPI Backend starting up...")
logger.info(f"📊 Database connected: {engine.url}")
logger.info(f"🔧 GCP AI enabled: {os.getenv('GCP_AI_ENABLED', 'false')}")
logger.info(f"🗂️ GCP credentials path: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'not set')}")

# Background task for AI analysis
def analyze_media_content(response_id: int, media_type: str, media_url: str):
    """Background task to analyze photo or video content using GCP AI services"""
    from database import get_db

    logger.info(f"🔄 Starting {media_type} analysis for response {response_id}")
    logger.info(f"📄 Media URL: {media_url}")

    # Get database session
    db = next(get_db())

    try:
        if media_type == "photo":
            logger.info(f"📷 Analyzing photo for response {response_id}...")
            # Analyze photo
            description = analyze_photo_response(media_url)
            logger.info(f"📷 Photo analysis result: {description[:100] if description else 'None'}...")

            if description:
                # Generate reporting labels using Gemini
                logger.info(f"🤖 Generating reporting labels for photo...")
                reporting_labels = generate_labels_for_media(description)
                logger.info(f"🏷️ Generated {len(reporting_labels) if reporting_labels else 0} labels")

                logger.info(f"💾 Saving photo analysis to database...")
                media_record = media_crud.create_or_update_media_analysis(
                    db=db,
                    response_id=response_id,
                    description=description,
                    reporting_labels=reporting_labels
                )
                logger.info(f"✅ Photo analysis saved with ID: {media_record.id}")
            else:
                logger.warning(f"⚠️ No description generated for photo response {response_id}")

        elif media_type == "video":
            logger.info(f"🎥 Analyzing video for response {response_id}...")
            # Analyze video
            description, transcript, brands = analyze_video_response(media_url)
            logger.info(f"🎥 Video analysis results:")
            logger.info(f"   📝 Description: {description[:100] if description else 'None'}...")
            logger.info(f"   🗣️ Transcript: {transcript[:100] if transcript else 'None'}...")
            logger.info(f"   🏷️ Brands: {brands if brands else 'None'}")

            if description or transcript or brands:
                # Generate reporting labels using Gemini
                logger.info(f"🤖 Generating reporting labels for video...")
                reporting_labels = generate_labels_for_media(description, transcript, brands)
                logger.info(f"🏷️ Generated {len(reporting_labels) if reporting_labels else 0} labels")

                logger.info(f"💾 Saving video analysis to database...")
                media_record = media_crud.create_or_update_media_analysis(
                    db=db,
                    response_id=response_id,
                    description=description,
                    transcript=transcript,
                    brands=brands,
                    reporting_labels=reporting_labels
                )
                logger.info(f"✅ Video analysis saved with ID: {media_record.id}")
            else:
                logger.warning(f"⚠️ No analysis results generated for video response {response_id}")

        logger.info(f"🎉 Completed {media_type} analysis for response {response_id}")

    except Exception as e:
        logger.error(f"❌ Background AI analysis failed for response {response_id}: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    finally:
        db.close()
        logger.info(f"🔚 Database connection closed for response {response_id}")

# CORS Configuration using Secret Manager
from secrets_manager import get_allowed_origins

allowed_origins_str = get_allowed_origins()
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

logger.info(f"✅ Configured CORS origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy", "database": "connected"}

# User endpoints
@app.post("/api/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    return crud.create_user(db=db, user=user)

@app.get("/api/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/users/{user_id}", response_model=schemas.UserWithPosts)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/api/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = crud.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Post endpoints
@app.post("/api/users/{user_id}/posts/", response_model=schemas.Post)
def create_post_for_user(user_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.create_post(db=db, post=post, author_id=user_id)

@app.get("/api/posts/", response_model=List[schemas.PostWithAuthor])
def read_posts(skip: int = 0, limit: int = 100, published_only: bool = False, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit, published_only=published_only)
    return posts

@app.get("/api/posts/{post_id}", response_model=schemas.PostWithAuthor)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@app.put("/api/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    db_post = crud.update_post(db=db, post_id=post_id, post=post)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    success = crud.delete_post(db=db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

# =============================================================================
# SURVEY ENDPOINTS
# =============================================================================

# Survey management endpoints
@app.post("/api/surveys/", response_model=survey_schemas.Survey)
def create_survey(survey: survey_schemas.SurveyCreate, db: Session = Depends(get_db)):
    return survey_crud.create_survey(db=db, survey=survey)

@app.get("/api/surveys/", response_model=List[survey_schemas.Survey])
def read_surveys(skip: int = 0, limit: int = 100, active_only: bool = True, db: Session = Depends(get_db)):
    surveys = survey_crud.get_surveys(db, skip=skip, limit=limit, active_only=active_only)
    return surveys

@app.get("/api/surveys/{survey_id}", response_model=survey_schemas.SurveyWithSubmissions)
def read_survey(survey_id: int, db: Session = Depends(get_db)):
    db_survey = survey_crud.get_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey

@app.get("/api/surveys/slug/{survey_slug}", response_model=survey_schemas.Survey)
def read_survey_by_slug(survey_slug: str, db: Session = Depends(get_db)):
    db_survey = survey_crud.get_survey_by_slug(db, survey_slug=survey_slug)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey

@app.put("/api/surveys/{survey_id}", response_model=survey_schemas.Survey)
def update_survey(survey_id: int, survey: survey_schemas.SurveyUpdate, db: Session = Depends(get_db)):
    db_survey = survey_crud.update_survey(db=db, survey_id=survey_id, survey=survey)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey

@app.delete("/api/surveys/{survey_id}")
def delete_survey(survey_id: int, db: Session = Depends(get_db)):
    success = survey_crud.delete_survey(db=db, survey_id=survey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Survey deleted successfully"}

# Survey submission endpoints
@app.post("/api/surveys/{survey_slug}/submit", response_model=survey_schemas.Submission)
def create_submission(survey_slug: str, submission_data: survey_schemas.SubmissionPersonalInfo, db: Session = Depends(get_db)):
    # Get survey by slug
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    if not survey.is_active:
        raise HTTPException(status_code=400, detail="Survey is not active")

    # Create submission
    submission = survey_schemas.SubmissionCreate(
        survey_id=survey.id,
        **submission_data.dict()
    )
    return survey_crud.create_submission(db=db, submission=submission)

@app.get("/api/submissions/{submission_id}", response_model=survey_schemas.SubmissionWithResponses)
def read_submission(submission_id: int, db: Session = Depends(get_db)):
    db_submission = survey_crud.get_submission(db, submission_id=submission_id)
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return db_submission

@app.get("/api/surveys/{survey_id}/submissions", response_model=List[survey_schemas.Submission])
def read_survey_submissions(survey_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    submissions = survey_crud.get_submissions_by_survey(db, survey_id=survey_id, skip=skip, limit=limit)
    return submissions

@app.put("/api/submissions/{submission_id}/complete")
def complete_submission(submission_id: int, db: Session = Depends(get_db)):
    db_submission = survey_crud.mark_submission_completed(db, submission_id)
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"message": "Submission marked as completed"}

# Survey response endpoints
@app.post("/api/submissions/{submission_id}/responses", response_model=survey_schemas.Response)
def create_response(submission_id: int, response: survey_schemas.ResponseCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Verify submission exists
    submission = survey_crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.is_completed:
        raise HTTPException(status_code=400, detail="Cannot add responses to completed submission")

    # Create response with submission_id
    response_create = survey_schemas.ResponseCreate(
        submission_id=submission_id,
        **response.dict(exclude_unset=True)
    )

    created_response = survey_crud.create_response(db=db, response=response_create)

    # Trigger AI analysis for photo/video responses
    if response.question_type == "photo" and response.photo_url:
        logger.info(f"📷 Queueing photo analysis for response {created_response.id}: {response.photo_url}")
        background_tasks.add_task(analyze_media_content, created_response.id, "photo", response.photo_url)
    elif response.question_type == "video" and response.video_url:
        logger.info(f"🎥 Queueing video analysis for response {created_response.id}: {response.video_url}")
        background_tasks.add_task(analyze_media_content, created_response.id, "video", response.video_url)
    else:
        logger.info(f"📝 Response {created_response.id} - no media to analyze (type: {response.question_type})")

    return created_response

@app.get("/api/submissions/{submission_id}/responses", response_model=List[survey_schemas.Response])
def read_submission_responses(submission_id: int, db: Session = Depends(get_db)):
    responses = survey_crud.get_responses_by_submission(db, submission_id=submission_id)
    return responses

@app.get("/api/submissions/{submission_id}/progress", response_model=survey_schemas.SurveyProgress)
def get_submission_progress(submission_id: int, db: Session = Depends(get_db)):
    progress = survey_crud.get_survey_progress(db, submission_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Submission not found")
    return progress

# File upload endpoints
@app.post("/api/surveys/{survey_slug}/upload/photo", response_model=survey_schemas.FileUploadResponse)
async def upload_photo(survey_slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verify survey exists
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

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

@app.post("/api/surveys/{survey_slug}/upload/video", response_model=survey_schemas.FileUploadResponse)
async def upload_video(survey_slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verify survey exists
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

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

# =============================================================================
# MEDIA ANALYSIS ENDPOINTS
# =============================================================================

@app.get("/api/responses/{response_id}/media-analysis", response_model=media_schemas.Media)
def get_response_media_analysis(response_id: int, db: Session = Depends(get_db)):
    """Get AI analysis for a specific response"""
    media_analysis = media_crud.get_media_by_response_id(db, response_id)
    if not media_analysis:
        raise HTTPException(status_code=404, detail="Media analysis not found")
    return media_analysis

@app.get("/api/media-analyses/", response_model=List[media_schemas.Media])
def get_all_media_analyses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all media analyses"""
    return media_crud.get_all_media_analyses(db, skip=skip, limit=limit)

@app.get("/api/surveys/{survey_id}/media-summary")
def get_survey_media_summary(survey_id: int, db: Session = Depends(get_db)):
    """Get a summary of all media analyses for a survey"""
    import json

    # Get all submissions for the survey
    submissions = survey_crud.get_submissions_by_survey(db, survey_id)

    total_analyses = 0
    photo_analyses = 0
    video_analyses = 0
    brands_detected = set()

    for submission in submissions:
        for response in submission.responses:
            if response.media_analysis:
                for media in response.media_analysis:
                    total_analyses += 1
                    if media.description and 'photo' in response.question_type.lower():
                        photo_analyses += 1
                    if media.transcript and 'video' in response.question_type.lower():
                        video_analyses += 1
                    if media.brands_detected:
                        try:
                            brands = json.loads(media.brands_detected)
                            brands_detected.update(brands)
                        except:
                            pass

    return {
        "survey_id": survey_id,
        "total_media_analyses": total_analyses,
        "photo_analyses": photo_analyses,
        "video_analyses": video_analyses,
        "unique_brands_detected": list(brands_detected),
        "brand_count": len(brands_detected)
    }

@app.post("/api/responses/{response_id}/trigger-analysis")
def trigger_media_analysis(response_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger AI analysis for a specific response - useful for testing"""

    logger.info(f"🔧 Manual trigger requested for response {response_id}")

    # Get the response
    response = survey_crud.get_response(db, response_id)
    if not response:
        logger.error(f"❌ Response {response_id} not found")
        raise HTTPException(status_code=404, detail="Response not found")

    logger.info(f"📋 Response {response_id} details: type={response.question_type}, photo_url={bool(response.photo_url)}, video_url={bool(response.video_url)}")

    # Check if it has media
    if response.question_type == "photo" and response.photo_url:
        logger.info(f"🔄 Manually triggering photo analysis for response {response_id}")
        logger.info(f"📷 Photo URL: {response.photo_url}")
        background_tasks.add_task(analyze_media_content, response_id, "photo", response.photo_url)
        return {"message": f"Photo analysis triggered for response {response_id}"}

    elif response.question_type == "video" and response.video_url:
        logger.info(f"🔄 Manually triggering video analysis for response {response_id}")
        logger.info(f"🎥 Video URL: {response.video_url}")
        background_tasks.add_task(analyze_media_content, response_id, "video", response.video_url)
        return {"message": f"Video analysis triggered for response {response_id}"}

    else:
        logger.warning(f"⚠️ Response {response_id} has no media to analyze (type: {response.question_type})")
        raise HTTPException(status_code=400, detail="Response has no media to analyze")

@app.get("/api/surveys/{survey_id}/reporting-labels")
def get_survey_reporting_labels(survey_id: int, db: Session = Depends(get_db)):
    """Get a frequency analysis of reporting labels for a survey"""
    return get_survey_label_summary(survey_id, db)

@app.get("/api/surveys/{survey_id}/label-summary")
def get_survey_label_analysis(survey_id: int, db: Session = Depends(get_db)):
    """Get comprehensive label analysis including AI-generated themes and insights"""
    from gemini_labeling import summarize_survey_labels
    return summarize_survey_labels(survey_id, db)

# =============================================================================
# REPORTING ENDPOINTS
# =============================================================================

@app.get("/api/reports/{survey_slug}/submissions")
def get_report_submissions(
    survey_slug: str,
    approved: Optional[bool] = None,
    sort_by: str = "submitted_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get submissions for reporting with filtering and sorting"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Build query - only include completed submissions
    query = db.query(survey_models.Submission).filter(
        survey_models.Submission.survey_id == survey.id,
        survey_models.Submission.is_completed == True
    )

    # Apply approved filter
    if approved is not None:
        query = query.filter(survey_models.Submission.is_approved == approved)

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

    # Get total count (only completed submissions)
    total_count = db.query(survey_models.Submission).filter(
        survey_models.Submission.survey_id == survey.id,
        survey_models.Submission.is_completed == True
    ).count()

    approved_count = db.query(survey_models.Submission).filter(
        survey_models.Submission.survey_id == survey.id,
        survey_models.Submission.is_completed == True,
        survey_models.Submission.is_approved == True
    ).count()

    return {
        "submissions": submissions,
        "total_count": total_count,
        "approved_count": approved_count,
        "rejected_count": total_count - approved_count,
        "survey": survey
    }

@app.get("/api/reports/{survey_slug}/submissions/{submission_id}")
def get_report_submission_detail(
    survey_slug: str,
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed submission with responses and media analysis for reporting"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Get submission
    submission = survey_crud.get_submission(db, submission_id)
    if not submission or submission.survey_id != survey.id:
        raise HTTPException(status_code=404, detail="Submission not found")

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
            for media in response.media_analysis:
                # Parse JSON strings
                import json
                brands_list = []
                labels_list = []

                if media.brands_detected:
                    try:
                        brands_list = json.loads(media.brands_detected)
                    except:
                        brands_list = []

                if media.reporting_labels:
                    try:
                        labels_list = json.loads(media.reporting_labels)
                    except:
                        labels_list = []

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

@app.put("/api/reports/{survey_slug}/submissions/{submission_id}/approve")
def approve_submission(
    survey_slug: str,
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Approve a submission"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Update submission
    submission = survey_crud.update_submission(
        db,
        submission_id,
        survey_schemas.SubmissionUpdate(is_approved=True)
    )
    if not submission or submission.survey_id != survey.id:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {"message": "Submission approved", "submission": submission}

@app.put("/api/reports/{survey_slug}/submissions/{submission_id}/reject")
def reject_submission(
    survey_slug: str,
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Reject a submission"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Update submission
    submission = survey_crud.update_submission(
        db,
        submission_id,
        survey_schemas.SubmissionUpdate(is_approved=False)
    )
    if not submission or submission.survey_id != survey.id:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {"message": "Submission rejected", "submission": submission}

@app.get("/api/reports/{survey_slug}/data", response_model=reporting_schemas.ReportingData)
def get_reporting_data(survey_slug: str, db: Session = Depends(get_db)):
    """Get comprehensive reporting data including demographics and question responses"""
    reporting_data = reporting_crud.get_reporting_data(db, survey_slug)

    if not reporting_data:
        raise HTTPException(status_code=404, detail="Survey not found")

    return reporting_data

@app.get("/api/reports/{survey_slug}/media-gallery", response_model=media_schemas.MediaGalleryResponse)
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

# =============================================================================
# SETTINGS ENDPOINTS
# =============================================================================

@app.get("/api/reports/{survey_slug}/settings")
def get_report_settings(survey_slug: str, db: Session = Depends(get_db)):
    """Get report settings for a survey"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Get settings with questions
    settings = settings_crud.get_report_settings_with_questions(db, survey.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    return settings

@app.put("/api/reports/{survey_slug}/settings/age-ranges")
def update_age_ranges(
    survey_slug: str,
    age_ranges_update: List[settings_schemas.AgeRange],
    db: Session = Depends(get_db)
):
    """Update age ranges for a survey"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Update age ranges
    settings_update = settings_schemas.ReportSettingsUpdate(age_ranges=age_ranges_update)
    updated_settings = settings_crud.update_report_settings(db, survey.id, settings_update)

    if not updated_settings:
        # Create settings if they don't exist
        updated_settings = settings_crud.create_or_get_report_settings(db, survey.id)
        updated_settings = settings_crud.update_report_settings(db, survey.id, settings_update)

    return {"message": "Age ranges updated successfully", "age_ranges": updated_settings.age_ranges}

@app.put("/api/reports/{survey_slug}/settings/question-display-names")
def update_question_display_names(
    survey_slug: str,
    updates: settings_schemas.BulkQuestionDisplayNameUpdate,
    db: Session = Depends(get_db)
):
    """Bulk update question display names for a survey"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

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

@app.put("/api/reports/{survey_slug}/settings/question-display-names/{question_id}")
def update_single_question_display_name(
    survey_slug: str,
    question_id: str,
    display_name_update: settings_schemas.QuestionDisplayNameUpdate,
    db: Session = Depends(get_db)
):
    """Update display name for a single question"""
    # Get survey
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

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

# =============================================================================
# MEDIA PROXY ENDPOINTS
# =============================================================================

from fastapi.responses import StreamingResponse, Response
from fastapi import Request
from google.cloud import storage
import io

@app.api_route("/api/media/proxy", methods=["GET", "HEAD"])
async def proxy_media(gcs_url: str, request: Request):
    """Proxy GCS media files for frontend consumption with video streaming support"""
    try:
        # Handle development mode simulated uploads
        if gcs_url.startswith('file://simulated-upload/'):
            # In development mode, return a placeholder image or video
            file_path = gcs_url.replace('file://simulated-upload/', '')

            # Determine content type based on file extension
            content_type = "application/octet-stream"
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
                # Return a simple SVG placeholder for images
                placeholder_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
                    <rect width="400" height="300" fill="#f0f0f0" stroke="#ccc" stroke-width="2"/>
                    <text x="200" y="120" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#666">📷 Simulated Photo</text>
                    <text x="200" y="150" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#999">Development Mode</text>
                    <text x="200" y="180" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#aaa">''' + file_path.split('/')[-1] + '''</text>
                </svg>'''
                return Response(
                    content=placeholder_content,
                    media_type="image/svg+xml",
                    headers={
                        "Cache-Control": "public, max-age=300",
                        "Access-Control-Allow-Origin": "http://localhost:3000",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Access-Control-Allow-Headers": "Range, Content-Range"
                    }
                )
            elif file_path.lower().endswith('.mp4'):
                content_type = "video/mp4"
                # For videos, return an SVG placeholder explaining it's simulated
                placeholder_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
                    <rect width="600" height="400" fill="#2a2a2a" stroke="#555" stroke-width="2"/>
                    <circle cx="300" cy="200" r="50" fill="#666" stroke="#999" stroke-width="2"/>
                    <polygon points="285,175 285,225 325,200" fill="#fff"/>
                    <text x="300" y="280" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#ccc">🎥 Simulated Video</text>
                    <text x="300" y="310" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#999">Development Mode</text>
                    <text x="300" y="340" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#777">''' + file_path.split('/')[-1] + '''</text>
                    <text x="300" y="360" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#555">This would be a real video in production</text>
                </svg>'''
                return Response(
                    content=placeholder_content,
                    media_type="image/svg+xml",
                    headers={
                        "Cache-Control": "public, max-age=300",
                        "Access-Control-Allow-Origin": "http://localhost:3000",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Access-Control-Allow-Headers": "Range, Content-Range"
                    }
                )
            else:
                return HTTPException(status_code=400, detail="Unsupported simulated file type")

        # Parse the GCS URL
        if not gcs_url.startswith('gs://'):
            raise HTTPException(status_code=400, detail="Invalid GCS URL")

        # Extract bucket and blob path
        url_parts = gcs_url.replace('gs://', '').split('/', 1)
        if len(url_parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid GCS URL format")

        bucket_name, blob_path = url_parts

        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        # Check if blob exists
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Media file not found")

        # Get blob size
        blob.reload()  # Ensure we have metadata
        file_size = blob.size

        # Determine content type based on file extension
        content_type = "application/octet-stream"
        if blob_path.lower().endswith(('.jpg', '.jpeg')):
            content_type = "image/jpeg"
        elif blob_path.lower().endswith('.png'):
            content_type = "image/png"
        elif blob_path.lower().endswith('.gif'):
            content_type = "image/gif"
        elif blob_path.lower().endswith('.mp4'):
            content_type = "video/mp4"
        elif blob_path.lower().endswith('.webm'):
            content_type = "video/webm"
        elif blob_path.lower().endswith('.mov'):
            content_type = "video/quicktime"

        # Handle HEAD requests - return headers only
        is_head_request = request.method == "HEAD"

        # Handle video streaming with range requests
        if content_type.startswith('video/'):
            range_header = request.headers.get('range')

            if range_header and not is_head_request:
                # Parse range header (e.g., "bytes=0-1023")
                range_match = range_header.replace('bytes=', '').split('-')
                start = int(range_match[0]) if range_match[0] else 0
                end = int(range_match[1]) if range_match[1] else file_size - 1

                # Ensure end doesn't exceed file size
                end = min(end, file_size - 1)
                content_length = end - start + 1

                # Download specific byte range (end is inclusive for GCS)
                blob_content = blob.download_as_bytes(start=start, end=end)

                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                    "Cache-Control": "public, max-age=3600",
                    "Content-Type": content_type,
                    "Access-Control-Allow-Origin": "http://localhost:3000",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Access-Control-Allow-Headers": "Range, Content-Range"
                }

                return Response(
                    content=blob_content,
                    status_code=206,  # Partial Content
                    headers=headers,
                    media_type=content_type
                )
            else:
                # No range request or HEAD request
                headers = {
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(file_size),
                    "Cache-Control": "public, max-age=3600",
                    "Content-Type": content_type,
                    "Access-Control-Allow-Origin": "http://localhost:3000",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Access-Control-Allow-Headers": "Range, Content-Range"
                }

                if is_head_request:
                    # HEAD request - headers only
                    return Response(
                        content="",
                        headers=headers,
                        media_type=content_type
                    )
                else:
                    # GET request - send entire file
                    blob_content = blob.download_as_bytes()
                    return Response(
                        content=blob_content,
                        headers=headers,
                        media_type=content_type
                    )
        else:
            # For images and other non-video content, use regular streaming
            blob_content = blob.download_as_bytes()

            return StreamingResponse(
                io.BytesIO(blob_content),
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Content-Disposition": f"inline; filename={blob_path.split('/')[-1]}",
                    "Content-Length": str(file_size)
                }
            )

    except Exception as e:
        logger.error(f"Media proxy error: {str(e)}")
        import traceback
        logger.error(f"Media proxy traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to load media")

@app.get("/api/debug/ai-status")
def get_ai_status():
    """Get the status of AI services for debugging"""
    from gcp_ai_analysis import gcp_ai_analyzer
    from gemini_labeling import gemini_labeler

    return {
        "gcp_ai_enabled": gcp_ai_analyzer.enabled,
        "vision_client": gcp_ai_analyzer.vision_client is not None,
        "video_client": gcp_ai_analyzer.video_client is not None,
        "gemini_enabled": gemini_labeler.enabled,
        "gemini_model": gemini_labeler.model is not None,
        "gcp_ai_env": os.getenv("GCP_AI_ENABLED", "false"),
        "gemini_env": os.getenv("GEMINI_ENABLED", "true"),
        "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "not set")
    }