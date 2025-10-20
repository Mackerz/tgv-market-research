"""Media Proxy Service for handling GCS file streaming"""
from fastapi import HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from google.cloud import storage
from typing import Optional, Tuple
import io
from app.utils.logging import get_context_logger

logger = get_context_logger(__name__)


class MediaProxyService:
    """
    Service for proxying media files from GCS to clients

    Handles:
    - Development mode simulation
    - GCS URL parsing
    - Content type detection
    - Range request support for video streaming
    - CORS headers
    """

    ALLOWED_ORIGINS = ["http://localhost:3000"]  # Can be configured via env

    def __init__(self):
        """Initialize GCS client"""
        try:
            self.storage_client = storage.Client()
            self.enabled = True
            logger.info_status("Media proxy service initialized")
        except Exception as e:
            logger.warning("GCS client init failed, using development mode", error=str(e))
            self.storage_client = None
            self.enabled = False

    def proxy_media(self, gcs_url: str, request: Request) -> Response:
        """
        Main entry point for media proxying

        Args:
            gcs_url: GCS URL (gs://...) or simulated URL
            request: FastAPI request object

        Returns:
            Response with media content

        Raises:
            HTTPException: For various error conditions
        """
        logger.debug("proxying media", url=gcs_url[:50])

        # Handle development mode
        if gcs_url.startswith('file://simulated-upload/'):
            return self._handle_simulated_media(gcs_url, request)

        # Validate and parse GCS URL
        bucket_name, blob_path = self._parse_gcs_url(gcs_url)

        # Get blob from GCS
        blob = self._get_blob(bucket_name, blob_path)

        # Determine content type
        content_type = self._get_content_type(blob_path)

        # Handle video streaming with range requests
        if content_type.startswith('video/'):
            return self._handle_video_streaming(blob, content_type, request)

        # Handle images and other content
        return self._handle_simple_media(blob, content_type)

    def _handle_simulated_media(self, gcs_url: str, request: Request) -> Response:
        """Handle development mode simulated uploads"""
        file_path = gcs_url.replace('file://simulated-upload/', '')

        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return self._create_photo_placeholder(file_path)
        elif file_path.lower().endswith('.mp4'):
            return self._create_video_placeholder(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported simulated file type")

    def _parse_gcs_url(self, gcs_url: str) -> Tuple[str, str]:
        """Parse GCS URL into bucket and blob path"""
        if not gcs_url.startswith('gs://'):
            raise HTTPException(status_code=400, detail="Invalid GCS URL")

        url_parts = gcs_url.replace('gs://', '').split('/', 1)
        if len(url_parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid GCS URL format")

        return url_parts[0], url_parts[1]

    def _get_blob(self, bucket_name: str, blob_path: str):
        """Get blob from GCS bucket"""
        if not self.enabled or not self.storage_client:
            raise HTTPException(status_code=503, detail="GCS not available")

        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            if not blob.exists():
                raise HTTPException(status_code=404, detail="Media file not found")

            blob.reload()  # Ensure we have metadata
            return blob

        except Exception as e:
            logger.error_failed("blob retrieval", e, bucket=bucket_name, path=blob_path)
            raise HTTPException(status_code=500, detail="Failed to retrieve media")

    def _get_content_type(self, file_path: str) -> str:
        """Determine content type from file extension"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mov': 'video/quicktime'
        }

        for ext, content_type in content_types.items():
            if file_path.lower().endswith(ext):
                return content_type

        return 'application/octet-stream'

    def _handle_video_streaming(self, blob, content_type: str, request: Request) -> Response:
        """Handle video streaming with range request support"""
        file_size = blob.size
        range_header = request.headers.get('range')
        is_head_request = request.method == "HEAD"

        headers = self._get_cors_headers()
        headers.update({
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Cache-Control": "public, max-age=3600",
            "Content-Type": content_type
        })

        # Handle HEAD request
        if is_head_request:
            return Response(content="", headers=headers, media_type=content_type)

        # Handle range request
        if range_header:
            return self._handle_range_request(blob, file_size, content_type, range_header, headers)

        # Return entire file
        blob_content = blob.download_as_bytes()
        return Response(content=blob_content, headers=headers, media_type=content_type)

    def _handle_range_request(
        self,
        blob,
        file_size: int,
        content_type: str,
        range_header: str,
        base_headers: dict
    ) -> Response:
        """Handle partial content request for video streaming"""
        # Parse range header (e.g., "bytes=0-1023")
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1

        # Ensure end doesn't exceed file size
        end = min(end, file_size - 1)
        content_length = end - start + 1

        # Download specific byte range
        blob_content = blob.download_as_bytes(start=start, end=end)

        headers = base_headers.copy()
        headers.update({
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Content-Length": str(content_length)
        })

        return Response(
            content=blob_content,
            status_code=206,  # Partial Content
            headers=headers,
            media_type=content_type
        )

    def _handle_simple_media(self, blob, content_type: str) -> StreamingResponse:
        """Handle images and other non-streaming content"""
        blob_content = blob.download_as_bytes()

        return StreamingResponse(
            io.BytesIO(blob_content),
            media_type=content_type,
            headers={
                **self._get_cors_headers(),
                "Cache-Control": "public, max-age=3600",
                "Content-Disposition": f"inline; filename={blob.name.split('/')[-1]}",
                "Content-Length": str(blob.size)
            }
        )

    def _get_cors_headers(self) -> dict:
        """Get CORS headers for media responses"""
        return {
            "Access-Control-Allow-Origin": self.ALLOWED_ORIGINS[0],
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Range, Content-Range"
        }

    def _create_photo_placeholder(self, file_path: str) -> Response:
        """Create SVG placeholder for photos in development mode"""
        filename = file_path.split('/')[-1]
        placeholder_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
            <rect width="400" height="300" fill="#f0f0f0" stroke="#ccc" stroke-width="2"/>
            <text x="200" y="120" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#666">📷 Simulated Photo</text>
            <text x="200" y="150" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#999">Development Mode</text>
            <text x="200" y="180" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#aaa">{filename}</text>
        </svg>'''

        return Response(
            content=placeholder_content,
            media_type="image/svg+xml",
            headers={**self._get_cors_headers(), "Cache-Control": "public, max-age=300"}
        )

    def _create_video_placeholder(self, file_path: str) -> Response:
        """Create SVG placeholder for videos in development mode"""
        filename = file_path.split('/')[-1]
        placeholder_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
            <rect width="600" height="400" fill="#2a2a2a" stroke="#555" stroke-width="2"/>
            <circle cx="300" cy="200" r="50" fill="#666" stroke="#999" stroke-width="2"/>
            <polygon points="285,175 285,225 325,200" fill="#fff"/>
            <text x="300" y="280" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#ccc">🎥 Simulated Video</text>
            <text x="300" y="310" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#999">Development Mode</text>
            <text x="300" y="340" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#777">{filename}</text>
            <text x="300" y="360" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#555">This would be a real video in production</text>
        </svg>'''

        return Response(
            content=placeholder_content,
            media_type="image/svg+xml",
            headers={**self._get_cors_headers(), "Cache-Control": "public, max-age=300"}
        )


# Global instance
_media_proxy_service: Optional[MediaProxyService] = None


def get_media_proxy_service() -> MediaProxyService:
    """Get or create media proxy service singleton"""
    global _media_proxy_service
    if _media_proxy_service is None:
        _media_proxy_service = MediaProxyService()
    return _media_proxy_service
