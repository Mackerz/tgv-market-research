"""Media Analysis Service - follows Single Responsibility Principle"""
from typing import Optional, List
from sqlalchemy.orm import Session
from utils.logging_utils import get_context_logger
import media_crud
from gcp_ai_analysis import analyze_photo_response, analyze_video_response
from gemini_labeling import generate_labels_for_media

logger = get_context_logger(__name__)


class MediaAnalysisService:
    """
    Service for analyzing photo and video media content

    Follows Single Responsibility Principle by separating:
    - Analysis orchestration
    - Individual media type handling
    - Database persistence
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def analyze_media(self, response_id: int, media_type: str, media_url: str):
        """
        Orchestrate media analysis based on type

        Args:
            response_id: Survey response ID
            media_type: Type of media ('photo' or 'video')
            media_url: GCS URL or file URL

        Returns:
            Media analysis record from database

        Raises:
            ValueError: If media_type is invalid
            Exception: If analysis or database operations fail
        """
        logger.info_start(
            "media analysis",
            response_id=response_id,
            media_type=media_type,
            media_url=media_url[:50] + "..."
        )

        try:
            if media_type == "photo":
                result = self._analyze_photo(response_id, media_url)
            elif media_type == "video":
                result = self._analyze_video(response_id, media_url)
            else:
                raise ValueError(f"Invalid media type: {media_type}")

            logger.info_complete(
                "media analysis",
                response_id=response_id,
                result_id=result.id if result else None
            )
            return result

        except Exception as e:
            logger.error_failed("media analysis", e, response_id=response_id)
            raise

    def _analyze_photo(self, response_id: int, photo_url: str):
        """
        Analyze photo content using GCP Vision API

        Args:
            response_id: Survey response ID
            photo_url: GCS URL of photo

        Returns:
            Media analysis record
        """
        logger.info_status("analyzing photo", response_id=response_id)

        # Get photo description from Vision API
        description = analyze_photo_response(photo_url)

        if not description:
            logger.warning("No description generated for photo", response_id=response_id)
            return None

        logger.debug("photo description", length=len(description), preview=description[:100])

        # Generate reporting labels using Gemini
        reporting_labels = self._generate_labels(description)

        # Save to database
        return self._save_analysis(
            response_id=response_id,
            description=description,
            reporting_labels=reporting_labels
        )

    def _analyze_video(self, response_id: int, video_url: str):
        """
        Analyze video content using GCP Video Intelligence API

        Args:
            response_id: Survey response ID
            video_url: GCS URL of video

        Returns:
            Media analysis record
        """
        logger.info_status("analyzing video", response_id=response_id)

        # Get video analysis from Video Intelligence API
        description, transcript, brands = analyze_video_response(video_url)

        if not any([description, transcript, brands]):
            logger.warning("No analysis results for video", response_id=response_id)
            return None

        logger.debug(
            "video analysis results",
            has_description=bool(description),
            has_transcript=bool(transcript),
            brand_count=len(brands) if brands else 0
        )

        # Generate reporting labels using Gemini
        reporting_labels = self._generate_labels(description, transcript, brands)

        # Save to database
        return self._save_analysis(
            response_id=response_id,
            description=description,
            transcript=transcript,
            brands=brands,
            reporting_labels=reporting_labels
        )

    def _generate_labels(
        self,
        description: str,
        transcript: Optional[str] = None,
        brands: Optional[List[str]] = None
    ) -> Optional[List[str]]:
        """
        Generate reporting labels using Gemini AI

        Args:
            description: Visual analysis description
            transcript: Optional audio transcript
            brands: Optional list of detected brands

        Returns:
            List of reporting labels or None
        """
        logger.info_status("generating reporting labels")

        try:
            labels = generate_labels_for_media(description, transcript, brands)
            if labels:
                logger.info_status("labels generated", count=len(labels))
            return labels
        except Exception as e:
            logger.error_failed("label generation", e)
            return None

    def _save_analysis(
        self,
        response_id: int,
        description: Optional[str] = None,
        transcript: Optional[str] = None,
        brands: Optional[List[str]] = None,
        reporting_labels: Optional[List[str]] = None
    ):
        """
        Save media analysis to database

        Args:
            response_id: Survey response ID
            description: Visual description
            transcript: Audio transcript (optional)
            brands: Detected brands (optional)
            reporting_labels: Generated labels (optional)

        Returns:
            Media analysis record
        """
        logger.info_status("saving analysis to database", response_id=response_id)

        try:
            media_record = media_crud.create_or_update_media_analysis(
                db=self.db,
                response_id=response_id,
                description=description,
                transcript=transcript,
                brands=brands,
                reporting_labels=reporting_labels
            )

            logger.info_complete(
                "analysis saved",
                response_id=response_id,
                media_id=media_record.id
            )
            return media_record

        except Exception as e:
            logger.error_failed("saving analysis", e, response_id=response_id)
            raise


def create_media_analysis_service(db: Session) -> MediaAnalysisService:
    """
    Factory function for creating MediaAnalysisService

    Args:
        db: Database session

    Returns:
        MediaAnalysisService instance
    """
    return MediaAnalysisService(db)
