"""Unit tests for MediaAnalysisService"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy.orm import Session

from app.services.media_analysis import (
    MediaAnalysisService,
    create_media_analysis_service,
    analyze_media_content_background
)
from app.models.survey import Response


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def media_analysis_service(mock_db):
    """Create MediaAnalysisService instance"""
    return MediaAnalysisService(mock_db)


@pytest.fixture
def mock_response():
    """Create a mock survey response"""
    response = Mock(spec=Response)
    response.id = 1
    response.photo_url = "gs://bucket/photo.jpg"
    response.video_url = None
    return response


class TestMediaAnalysisServiceInit:
    """Tests for MediaAnalysisService initialization"""

    def test_initialization(self, mock_db):
        """Test service initializes with database session"""
        service = MediaAnalysisService(mock_db)
        assert service.db == mock_db


class TestAnalyzeMedia:
    """Tests for analyze_media orchestration method"""

    @patch('app.services.media_analysis.MediaAnalysisService._analyze_photo')
    def test_analyze_photo(self, mock_analyze_photo, media_analysis_service):
        """Test analyze_media routes photo to _analyze_photo"""
        mock_result = MagicMock()
        mock_analyze_photo.return_value = mock_result

        result = media_analysis_service.analyze_media(
            response_id=1,
            media_type="photo",
            media_url="gs://bucket/photo.jpg"
        )

        mock_analyze_photo.assert_called_once_with(1, "gs://bucket/photo.jpg")
        assert result == mock_result

    @patch('app.services.media_analysis.MediaAnalysisService._analyze_video')
    def test_analyze_video(self, mock_analyze_video, media_analysis_service):
        """Test analyze_media routes video to _analyze_video"""
        mock_result = MagicMock()
        mock_analyze_video.return_value = mock_result

        result = media_analysis_service.analyze_media(
            response_id=1,
            media_type="video",
            media_url="gs://bucket/video.mp4"
        )

        mock_analyze_video.assert_called_once_with(1, "gs://bucket/video.mp4")
        assert result == mock_result

    def test_analyze_invalid_media_type(self, media_analysis_service):
        """Test analyze_media raises ValueError for invalid media type"""
        with pytest.raises(ValueError) as exc_info:
            media_analysis_service.analyze_media(
                response_id=1,
                media_type="audio",
                media_url="gs://bucket/audio.mp3"
            )

        assert "Invalid media type" in str(exc_info.value)

    @patch('app.services.media_analysis.MediaAnalysisService._analyze_photo')
    def test_analyze_media_exception_handling(self, mock_analyze_photo, media_analysis_service):
        """Test analyze_media handles exceptions from analysis"""
        mock_analyze_photo.side_effect = Exception("Analysis failed")

        with pytest.raises(Exception) as exc_info:
            media_analysis_service.analyze_media(
                response_id=1,
                media_type="photo",
                media_url="gs://bucket/photo.jpg"
            )

        assert "Analysis failed" in str(exc_info.value)


class TestAnalyzePhoto:
    """Tests for photo analysis"""

    @patch('app.services.media_analysis.analyze_photo_response')
    @patch('app.services.media_analysis.MediaAnalysisService._generate_labels')
    @patch('app.services.media_analysis.MediaAnalysisService._save_analysis')
    def test_analyze_photo_success(
        self,
        mock_save,
        mock_generate_labels,
        mock_vision_api,
        media_analysis_service
    ):
        """Test successful photo analysis"""
        mock_vision_api.return_value = "A can of Monster Energy drink on a table"
        mock_generate_labels.return_value = ["beverage", "energy_drink", "aluminum_can"]
        mock_media_record = MagicMock()
        mock_save.return_value = mock_media_record

        result = media_analysis_service._analyze_photo(1, "gs://bucket/photo.jpg")

        mock_vision_api.assert_called_once_with("gs://bucket/photo.jpg")
        mock_generate_labels.assert_called_once_with("A can of Monster Energy drink on a table")
        mock_save.assert_called_once_with(
            response_id=1,
            description="A can of Monster Energy drink on a table",
            reporting_labels=["beverage", "energy_drink", "aluminum_can"]
        )
        assert result == mock_media_record

    @patch('app.services.media_analysis.analyze_photo_response')
    def test_analyze_photo_no_description(self, mock_vision_api, media_analysis_service):
        """Test photo analysis when Vision API returns no description"""
        mock_vision_api.return_value = None

        result = media_analysis_service._analyze_photo(1, "gs://bucket/photo.jpg")

        assert result is None

    @patch('app.services.media_analysis.analyze_photo_response')
    def test_analyze_photo_empty_description(self, mock_vision_api, media_analysis_service):
        """Test photo analysis when Vision API returns empty string"""
        mock_vision_api.return_value = ""

        result = media_analysis_service._analyze_photo(1, "gs://bucket/photo.jpg")

        assert result is None


class TestAnalyzeVideo:
    """Tests for video analysis"""

    @patch('app.services.media_analysis.analyze_video_response')
    @patch('app.services.media_analysis.MediaAnalysisService._generate_labels')
    @patch('app.services.media_analysis.MediaAnalysisService._save_analysis')
    def test_analyze_video_success(
        self,
        mock_save,
        mock_generate_labels,
        mock_video_api,
        media_analysis_service
    ):
        """Test successful video analysis"""
        mock_video_api.return_value = (
            "Video shows person drinking Monster Energy",
            "I love Monster Energy drinks",
            ["Monster Energy"]
        )
        mock_generate_labels.return_value = ["beverage", "testimonial", "brand_awareness"]
        mock_media_record = MagicMock()
        mock_save.return_value = mock_media_record

        result = media_analysis_service._analyze_video(1, "gs://bucket/video.mp4")

        mock_video_api.assert_called_once_with("gs://bucket/video.mp4")
        mock_generate_labels.assert_called_once_with(
            "Video shows person drinking Monster Energy",
            "I love Monster Energy drinks",
            ["Monster Energy"]
        )
        mock_save.assert_called_once_with(
            response_id=1,
            description="Video shows person drinking Monster Energy",
            transcript="I love Monster Energy drinks",
            brands=["Monster Energy"],
            reporting_labels=["beverage", "testimonial", "brand_awareness"]
        )
        assert result == mock_media_record

    @patch('app.services.media_analysis.analyze_video_response')
    def test_analyze_video_no_results(self, mock_video_api, media_analysis_service):
        """Test video analysis when Video Intelligence returns no results"""
        mock_video_api.return_value = (None, None, None)

        result = media_analysis_service._analyze_video(1, "gs://bucket/video.mp4")

        assert result is None

    @patch('app.services.media_analysis.analyze_video_response')
    def test_analyze_video_partial_results(self, mock_video_api, media_analysis_service):
        """Test video analysis with partial results (transcript only)"""
        mock_video_api.return_value = (None, "I love this product", None)

        # Should not return None because transcript is present
        with patch.object(media_analysis_service, '_generate_labels', return_value=["positive_sentiment"]):
            with patch.object(media_analysis_service, '_save_analysis', return_value=MagicMock()) as mock_save:
                result = media_analysis_service._analyze_video(1, "gs://bucket/video.mp4")

                assert result is not None
                mock_save.assert_called_once()


class TestGenerateLabels:
    """Tests for label generation using Gemini"""

    @patch('app.services.media_analysis.generate_labels_for_media')
    def test_generate_labels_success(self, mock_gemini, media_analysis_service):
        """Test successful label generation"""
        mock_gemini.return_value = ["label1", "label2", "label3"]

        labels = media_analysis_service._generate_labels(
            description="Test description",
            transcript="Test transcript",
            brands=["Brand A"]
        )

        mock_gemini.assert_called_once_with("Test description", "Test transcript", ["Brand A"])
        assert labels == ["label1", "label2", "label3"]

    @patch('app.services.media_analysis.generate_labels_for_media')
    def test_generate_labels_no_transcript_or_brands(self, mock_gemini, media_analysis_service):
        """Test label generation with description only"""
        mock_gemini.return_value = ["label1"]

        labels = media_analysis_service._generate_labels(description="Test description")

        mock_gemini.assert_called_once_with("Test description", None, None)
        assert labels == ["label1"]

    @patch('app.services.media_analysis.generate_labels_for_media')
    def test_generate_labels_empty_result(self, mock_gemini, media_analysis_service):
        """Test label generation when Gemini returns empty list"""
        mock_gemini.return_value = []

        labels = media_analysis_service._generate_labels(description="Test description")

        assert labels == []

    @patch('app.services.media_analysis.generate_labels_for_media')
    def test_generate_labels_exception_handling(self, mock_gemini, media_analysis_service):
        """Test label generation handles exceptions gracefully"""
        mock_gemini.side_effect = Exception("Gemini API error")

        labels = media_analysis_service._generate_labels(description="Test description")

        assert labels is None


class TestSaveAnalysis:
    """Tests for saving analysis to database"""

    @patch('app.services.media_analysis.media_crud.create_or_update_media_analysis')
    def test_save_analysis_full_data(self, mock_crud, media_analysis_service):
        """Test saving analysis with all fields"""
        mock_media_record = MagicMock()
        mock_media_record.id = 123
        mock_crud.return_value = mock_media_record

        result = media_analysis_service._save_analysis(
            response_id=1,
            description="Test description",
            transcript="Test transcript",
            brands=["Brand A", "Brand B"],
            reporting_labels=["label1", "label2"]
        )

        mock_crud.assert_called_once_with(
            db=media_analysis_service.db,
            response_id=1,
            description="Test description",
            transcript="Test transcript",
            brands=["Brand A", "Brand B"],
            reporting_labels=["label1", "label2"]
        )
        assert result == mock_media_record

    @patch('app.services.media_analysis.media_crud.create_or_update_media_analysis')
    def test_save_analysis_minimal_data(self, mock_crud, media_analysis_service):
        """Test saving analysis with minimal fields"""
        mock_media_record = MagicMock()
        mock_crud.return_value = mock_media_record

        result = media_analysis_service._save_analysis(
            response_id=1,
            description="Test description"
        )

        mock_crud.assert_called_once_with(
            db=media_analysis_service.db,
            response_id=1,
            description="Test description",
            transcript=None,
            brands=None,
            reporting_labels=None
        )
        assert result == mock_media_record

    @patch('app.services.media_analysis.media_crud.create_or_update_media_analysis')
    def test_save_analysis_exception_handling(self, mock_crud, media_analysis_service):
        """Test save_analysis handles database errors"""
        mock_crud.side_effect = Exception("Database error")

        with pytest.raises(Exception) as exc_info:
            media_analysis_service._save_analysis(
                response_id=1,
                description="Test description"
            )

        assert "Database error" in str(exc_info.value)


class TestFactoryFunction:
    """Tests for factory function"""

    def test_create_media_analysis_service(self, mock_db):
        """Test factory function creates service"""
        service = create_media_analysis_service(mock_db)

        assert isinstance(service, MediaAnalysisService)
        assert service.db == mock_db


class TestBackgroundTask:
    """Tests for background task function"""

    @patch('app.core.database.SessionLocal')
    @patch('app.services.media_analysis.MediaAnalysisService')
    def test_background_task_photo(self, mock_service_class, mock_session_local):
        """Test background task with photo response"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_response = MagicMock()
        mock_response.id = 1
        mock_response.photo_url = "gs://bucket/photo.jpg"
        mock_response.video_url = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_response

        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        analyze_media_content_background(response_id=1)

        mock_db.query.assert_called_once()
        mock_service_class.assert_called_once_with(mock_db)
        mock_service.analyze_media.assert_called_once_with(1, "photo", "gs://bucket/photo.jpg")
        mock_db.close.assert_called_once()

    @patch('app.core.database.SessionLocal')
    @patch('app.services.media_analysis.MediaAnalysisService')
    def test_background_task_video(self, mock_service_class, mock_session_local):
        """Test background task with video response"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_response = MagicMock()
        mock_response.id = 1
        mock_response.photo_url = None
        mock_response.video_url = "gs://bucket/video.mp4"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_response

        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        analyze_media_content_background(response_id=1)

        mock_service.analyze_media.assert_called_once_with(1, "video", "gs://bucket/video.mp4")
        mock_db.close.assert_called_once()

    @patch('app.core.database.SessionLocal')
    def test_background_task_response_not_found(self, mock_session_local):
        """Test background task when response not found"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Should not raise exception
        analyze_media_content_background(response_id=999)

        mock_db.close.assert_called_once()

    @patch('app.core.database.SessionLocal')
    def test_background_task_no_media(self, mock_session_local):
        """Test background task when response has no media"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_response = MagicMock()
        mock_response.id = 1
        mock_response.photo_url = None
        mock_response.video_url = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_response

        # Should not raise exception
        analyze_media_content_background(response_id=1)

        mock_db.close.assert_called_once()

    @patch('app.core.database.SessionLocal')
    @patch('app.services.media_analysis.MediaAnalysisService')
    def test_background_task_exception_handling(self, mock_service_class, mock_session_local):
        """Test background task handles exceptions and closes DB"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_response = MagicMock()
        mock_response.id = 1
        mock_response.photo_url = "gs://bucket/photo.jpg"
        mock_response.video_url = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_response

        mock_service = MagicMock()
        mock_service.analyze_media.side_effect = Exception("Analysis failed")
        mock_service_class.return_value = mock_service

        with pytest.raises(Exception) as exc_info:
            analyze_media_content_background(response_id=1)

        assert "Analysis failed" in str(exc_info.value)
        # Ensure DB is closed even on exception
        mock_db.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
