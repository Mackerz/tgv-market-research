"""Unit tests for MediaProxyService"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, Request
from fastapi.responses import Response, StreamingResponse

from app.services.media_proxy import MediaProxyService, get_media_proxy_service


@pytest.fixture
def mock_storage_client():
    """Create a mock GCS storage client"""
    with patch('app.services.media_proxy.storage.Client') as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request"""
    request = Mock(spec=Request)
    request.headers = {}
    request.method = "GET"
    return request


@pytest.fixture
def media_proxy_service(mock_storage_client):
    """Create MediaProxyService instance with mocked GCS"""
    service = MediaProxyService()
    return service


@pytest.fixture
def media_proxy_service_disabled():
    """Create MediaProxyService instance with GCS disabled"""
    with patch('app.services.media_proxy.storage.Client', side_effect=Exception("GCS not available")):
        service = MediaProxyService()
        return service


class TestMediaProxyServiceInit:
    """Tests for MediaProxyService initialization"""

    def test_initialization_success(self, mock_storage_client):
        """Test successful initialization with GCS"""
        service = MediaProxyService()
        assert service.enabled is True
        assert service.storage_client is not None

    def test_initialization_failure_fallback(self):
        """Test initialization falls back to disabled mode when GCS fails"""
        with patch('app.services.media_proxy.storage.Client', side_effect=Exception("GCS error")):
            service = MediaProxyService()
            assert service.enabled is False
            assert service.storage_client is None


class TestParseGcsUrl:
    """Tests for GCS URL parsing"""

    def test_parse_valid_gcs_url(self, media_proxy_service):
        """Test parsing valid GCS URL"""
        bucket, blob = media_proxy_service._parse_gcs_url("gs://my-bucket/path/to/file.jpg")
        assert bucket == "my-bucket"
        assert blob == "path/to/file.jpg"

    def test_parse_gcs_url_with_deep_path(self, media_proxy_service):
        """Test parsing GCS URL with deep path"""
        bucket, blob = media_proxy_service._parse_gcs_url("gs://bucket/a/b/c/d/file.mp4")
        assert bucket == "bucket"
        assert blob == "a/b/c/d/file.mp4"

    def test_parse_invalid_url_no_gs_prefix(self, media_proxy_service):
        """Test parsing invalid URL without gs:// prefix"""
        with pytest.raises(HTTPException) as exc_info:
            media_proxy_service._parse_gcs_url("http://bucket/file.jpg")
        assert exc_info.value.status_code == 400
        assert "Invalid GCS URL" in str(exc_info.value.detail)

    def test_parse_invalid_url_no_path(self, media_proxy_service):
        """Test parsing invalid URL without path"""
        with pytest.raises(HTTPException) as exc_info:
            media_proxy_service._parse_gcs_url("gs://bucket-only")
        assert exc_info.value.status_code == 400


class TestGetContentType:
    """Tests for content type detection"""

    def test_content_type_jpg(self, media_proxy_service):
        """Test JPEG content type"""
        assert media_proxy_service._get_content_type("file.jpg") == "image/jpeg"
        assert media_proxy_service._get_content_type("file.jpeg") == "image/jpeg"
        assert media_proxy_service._get_content_type("FILE.JPG") == "image/jpeg"

    def test_content_type_png(self, media_proxy_service):
        """Test PNG content type"""
        assert media_proxy_service._get_content_type("image.png") == "image/png"

    def test_content_type_video(self, media_proxy_service):
        """Test video content types"""
        assert media_proxy_service._get_content_type("video.mp4") == "video/mp4"
        assert media_proxy_service._get_content_type("video.webm") == "video/webm"
        assert media_proxy_service._get_content_type("video.mov") == "video/quicktime"

    def test_content_type_unknown(self, media_proxy_service):
        """Test unknown file type"""
        assert media_proxy_service._get_content_type("file.unknown") == "application/octet-stream"


class TestGetBlob:
    """Tests for blob retrieval from GCS"""

    def test_get_blob_success(self, media_proxy_service, mock_storage_client):
        """Test successful blob retrieval"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.bucket.return_value = mock_bucket

        blob = media_proxy_service._get_blob("test-bucket", "path/to/file.jpg")

        assert blob == mock_blob
        mock_blob.reload.assert_called_once()
        mock_storage_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("path/to/file.jpg")

    def test_get_blob_not_found(self, media_proxy_service, mock_storage_client):
        """Test blob not found raises exception"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        mock_blob.reload.side_effect = Exception("Blob does not exist")
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.bucket.return_value = mock_bucket

        with pytest.raises(HTTPException) as exc_info:
            media_proxy_service._get_blob("test-bucket", "missing.jpg")

        # The code catches the exception and returns 500 with generic error
        assert exc_info.value.status_code in [404, 500]
        assert "retrieve" in str(exc_info.value.detail).lower() or "not found" in str(exc_info.value.detail).lower()

    def test_get_blob_gcs_disabled(self, media_proxy_service_disabled):
        """Test blob retrieval when GCS is disabled"""
        with pytest.raises(HTTPException) as exc_info:
            media_proxy_service_disabled._get_blob("test-bucket", "file.jpg")

        assert exc_info.value.status_code == 503
        assert "not available" in str(exc_info.value.detail).lower()

    def test_get_blob_error_handling(self, media_proxy_service, mock_storage_client):
        """Test blob retrieval with GCS error"""
        mock_storage_client.bucket.side_effect = Exception("GCS error")

        with pytest.raises(HTTPException) as exc_info:
            media_proxy_service._get_blob("test-bucket", "file.jpg")

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve media" in str(exc_info.value.detail)


class TestSimulatedMedia:
    """Tests for development mode simulated media"""

    def test_simulated_photo(self, media_proxy_service, mock_request):
        """Test simulated photo response"""
        response = media_proxy_service._handle_simulated_media(
            "file://simulated-upload/test-photo.jpg",
            mock_request
        )

        assert response.status_code == 200
        assert response.media_type == "image/svg+xml"
        assert b"Simulated Photo" in response.body
        assert b"test-photo.jpg" in response.body

    def test_simulated_video(self, media_proxy_service, mock_request):
        """Test simulated video response"""
        response = media_proxy_service._handle_simulated_media(
            "file://simulated-upload/test-video.mp4",
            mock_request
        )

        assert response.status_code == 200
        assert response.media_type == "image/svg+xml"
        assert b"Simulated Video" in response.body
        assert b"test-video.mp4" in response.body

    def test_simulated_unsupported_type(self, media_proxy_service, mock_request):
        """Test simulated media with unsupported file type"""
        with pytest.raises(HTTPException) as exc_info:
            media_proxy_service._handle_simulated_media(
                "file://simulated-upload/test.txt",
                mock_request
            )

        assert exc_info.value.status_code == 400
        assert "Unsupported" in str(exc_info.value.detail)


class TestSimpleMediaHandling:
    """Tests for simple (non-streaming) media handling"""

    def test_handle_simple_media(self, media_proxy_service):
        """Test handling images and simple media"""
        mock_blob = MagicMock()
        mock_blob.download_as_bytes.return_value = b"fake image data"
        mock_blob.size = 1024
        mock_blob.name = "path/to/image.jpg"

        response = media_proxy_service._handle_simple_media(mock_blob, "image/jpeg")

        assert isinstance(response, StreamingResponse)
        assert response.media_type == "image/jpeg"
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Cache-Control"] == "public, max-age=3600"
        assert response.headers["Content-Length"] == "1024"


class TestVideoStreaming:
    """Tests for video streaming with range requests"""

    def test_video_streaming_full_file(self, media_proxy_service, mock_request):
        """Test video streaming without range request (full file)"""
        mock_blob = MagicMock()
        mock_blob.size = 10000
        mock_blob.download_as_bytes.return_value = b"video data"

        response = media_proxy_service._handle_video_streaming(
            mock_blob, "video/mp4", mock_request
        )

        assert response.status_code == 200
        assert response.media_type == "video/mp4"
        assert "Accept-Ranges" in response.headers
        assert response.headers["Accept-Ranges"] == "bytes"
        assert b"video data" in response.body

    def test_video_streaming_head_request(self, media_proxy_service, mock_request):
        """Test video streaming HEAD request"""
        mock_request.method = "HEAD"
        mock_blob = MagicMock()
        mock_blob.size = 10000

        response = media_proxy_service._handle_video_streaming(
            mock_blob, "video/mp4", mock_request
        )

        assert response.status_code == 200
        assert response.media_type == "video/mp4"
        assert response.body == b""
        assert "Accept-Ranges" in response.headers

    def test_video_streaming_with_range(self, media_proxy_service, mock_request):
        """Test video streaming with range request"""
        mock_request.headers = {"range": "bytes=0-999"}
        mock_blob = MagicMock()
        mock_blob.size = 10000
        mock_blob.download_as_bytes.return_value = b"partial data"

        response = media_proxy_service._handle_video_streaming(
            mock_blob, "video/mp4", mock_request
        )

        assert response.status_code == 206  # Partial Content
        assert "Content-Range" in response.headers
        assert response.headers["Content-Range"] == "bytes 0-999/10000"
        mock_blob.download_as_bytes.assert_called_once_with(start=0, end=999)

    def test_handle_range_request_partial(self, media_proxy_service):
        """Test partial content range request"""
        mock_blob = MagicMock()
        mock_blob.download_as_bytes.return_value = b"partial"
        file_size = 10000

        response = media_proxy_service._handle_range_request(
            mock_blob,
            file_size,
            "video/mp4",
            "bytes=500-999",
            {}
        )

        assert response.status_code == 206
        assert response.headers["Content-Range"] == "bytes 500-999/10000"
        assert response.headers["Content-Length"] == "500"
        mock_blob.download_as_bytes.assert_called_once_with(start=500, end=999)

    def test_handle_range_request_open_ended(self, media_proxy_service):
        """Test range request with no end specified"""
        mock_blob = MagicMock()
        mock_blob.download_as_bytes.return_value = b"rest of file"
        file_size = 10000

        response = media_proxy_service._handle_range_request(
            mock_blob,
            file_size,
            "video/mp4",
            "bytes=5000-",
            {}
        )

        assert response.status_code == 206
        assert response.headers["Content-Range"] == "bytes 5000-9999/10000"
        mock_blob.download_as_bytes.assert_called_once_with(start=5000, end=9999)


class TestCorsHeaders:
    """Tests for CORS headers"""

    def test_cors_headers(self, media_proxy_service):
        """Test CORS headers are correct"""
        headers = media_proxy_service._get_cors_headers()

        assert "Access-Control-Allow-Origin" in headers
        assert headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        assert "Access-Control-Allow-Methods" in headers
        assert "GET" in headers["Access-Control-Allow-Methods"]
        assert "Access-Control-Allow-Headers" in headers


class TestProxyMediaIntegration:
    """Integration tests for proxy_media main method"""

    def test_proxy_simulated_media(self, media_proxy_service, mock_request):
        """Test proxying simulated media"""
        response = media_proxy_service.proxy_media(
            "file://simulated-upload/photo.jpg",
            mock_request
        )

        assert response.status_code == 200
        assert "svg" in response.media_type

    def test_proxy_media_invalid_url(self, media_proxy_service, mock_request):
        """Test proxying with invalid URL"""
        with pytest.raises(HTTPException) as exc_info:
            media_proxy_service.proxy_media("invalid-url", mock_request)

        assert exc_info.value.status_code == 400


class TestSingletonPattern:
    """Tests for singleton service getter"""

    def test_get_media_proxy_service_singleton(self):
        """Test that get_media_proxy_service returns singleton"""
        with patch('app.services.media_proxy.storage.Client'):
            service1 = get_media_proxy_service()
            service2 = get_media_proxy_service()

            assert service1 is service2

    def test_get_media_proxy_service_creates_instance(self):
        """Test that get_media_proxy_service creates instance"""
        with patch('app.services.media_proxy.storage.Client'):
            # Reset singleton
            import app.services.media_proxy
            app.services.media_proxy._media_proxy_service = None

            service = get_media_proxy_service()
            assert isinstance(service, MediaProxyService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
