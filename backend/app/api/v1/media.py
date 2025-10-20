"""Media Analysis API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import List
import logging
import os

from app.core.database import get_db
from app.schemas import media as media_schemas
from app.crud import media as media_crud
from app.crud import survey as survey_crud
from app.integrations.gcp.gemini import get_survey_label_summary, summarize_survey_labels
from app.dependencies import get_response_or_404

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["media"])


# Background task for AI analysis
def analyze_media_content(response_id: int, media_type: str, media_url: str):
    """Background task to analyze photo or video content using GCP AI services"""
    from app.core.database import get_db
    from app.services.media_analysis import create_media_analysis_service

    # Get database session
    db = next(get_db())

    try:
        # Use MediaAnalysisService for cleaner separation of concerns
        service = create_media_analysis_service(db)
        service.analyze_media(response_id, media_type, media_url)
    except Exception as e:
        logger.error(f"❌ Background AI analysis failed for response {response_id}: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    finally:
        db.close()


# =============================================================================
# MEDIA ANALYSIS ENDPOINTS
# =============================================================================

@router.get("/responses/{response_id}/media-analysis", response_model=media_schemas.Media)
def get_response_media_analysis(response_id: int, db: Session = Depends(get_db)):
    """Get AI analysis for a specific response"""
    media_analysis = media_crud.get_media_by_response_id(db, response_id)
    if not media_analysis:
        raise HTTPException(status_code=404, detail="Media analysis not found")
    return media_analysis


@router.get("/media-analyses/", response_model=List[media_schemas.Media])
def get_all_media_analyses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all media analyses"""
    return media_crud.get_all_media_analyses(db, skip=skip, limit=limit)


@router.get("/surveys/{survey_id}/media-summary")
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


@router.post("/responses/{response_id}/trigger-analysis")
def trigger_media_analysis(response_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger AI analysis for a specific response - useful for testing"""

    logger.info(f"🔧 Manual trigger requested for response {response_id}")

    # Get the response using dependency helper
    response = get_response_or_404(response_id, db)

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


@router.get("/surveys/{survey_id}/reporting-labels")
def get_survey_reporting_labels(survey_id: int, db: Session = Depends(get_db)):
    """Get a frequency analysis of reporting labels for a survey"""
    return get_survey_label_summary(survey_id, db)


@router.get("/surveys/{survey_id}/label-summary")
def get_survey_label_analysis(survey_id: int, db: Session = Depends(get_db)):
    """Get comprehensive label analysis including AI-generated themes and insights"""
    return summarize_survey_labels(survey_id, db)


# =============================================================================
# MEDIA PROXY ENDPOINTS
# =============================================================================

@router.api_route("/media/proxy", methods=["GET", "HEAD"])
async def proxy_media(gcs_url: str, request: Request):
    """Proxy GCS media files for frontend consumption with video streaming support"""
    from app.services.media_proxy import get_media_proxy_service

    try:
        service = get_media_proxy_service()
        return service.proxy_media(gcs_url, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media proxy error: {str(e)}")
        import traceback
        logger.error(f"Media proxy traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to load media")


# =============================================================================
# DEBUG ENDPOINTS
# =============================================================================

@router.get("/debug/ai-status")
def get_ai_status():
    """Get the status of AI services for debugging"""
    from app.integrations.gcp.vision import gcp_ai_analyzer
    from app.integrations.gcp.gemini import gemini_labeler

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
