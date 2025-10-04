from google.cloud import storage
import os
from typing import Optional
import uuid
import tempfile
from PIL import Image
import io
from fastapi import UploadFile

class GCPStorageManager:
    def __init__(self):
        # Import secrets manager
        from secrets_manager import get_gcp_project_id, get_gcs_bucket_name

        self.enabled = os.getenv("GCP_STORAGE_ENABLED", "false").lower() == "true"

        if not self.enabled:
            print("⚠️  GCP Storage is disabled. Photo/video uploads will be simulated.")
            self.client = None
            self.photo_bucket = None
            self.video_bucket = None
            return

        # Use secrets manager for configuration
        bucket_name = get_gcs_bucket_name()
        self.photo_bucket_name = bucket_name or os.getenv("GCP_STORAGE_BUCKET_PHOTOS", "survey-photos-bucket")
        self.video_bucket_name = bucket_name or os.getenv("GCP_STORAGE_BUCKET_VIDEOS", "survey-videos-bucket")
        self.project_id = get_gcp_project_id() or os.getenv("GCP_PROJECT_ID", "your-project-id")

        try:
            # Initialize client - will use service account key if provided
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                print(f"🔑 Using service account key: {credentials_path}")
                self.client = storage.Client.from_service_account_json(credentials_path)
            else:
                # Will use default credentials (useful in GCP environment)
                print(f"🔑 Using default credentials for project: {self.project_id}")
                self.client = storage.Client(project=self.project_id)

            self.photo_bucket = self.client.bucket(self.photo_bucket_name)
            self.video_bucket = self.client.bucket(self.video_bucket_name)
            print(f"✅ GCP Storage initialized:")
            print(f"   📷 Photos: {self.photo_bucket_name}")
            print(f"   🎥 Videos: {self.video_bucket_name}")
        except Exception as e:
            print(f"❌ GCP Storage initialization failed: {e}")
            print("🔧 Falling back to development mode (uploads simulated)")
            self.enabled = False
            self.client = None
            self.photo_bucket = None
            self.video_bucket = None

    def _upload_to_bucket(self, file: UploadFile, survey_slug: str, file_id: str, bucket, bucket_name: str) -> str:
        """
        Upload a file to a specific GCP Storage bucket
        Returns the public URL of the uploaded file
        """
        # Get file extension
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'

        # Create storage path
        storage_path = f"{survey_slug}/{file_id}.{file_extension}"

        if not self.enabled or not bucket:
            # Development mode - return a simulated URL
            print(f"📁 Simulating upload: {file.filename} -> {bucket_name}/{storage_path}")
            return f"file://simulated-upload/{bucket_name}/{storage_path}"

        # Create blob and upload
        blob = bucket.blob(storage_path)

        # Set content type based on file extension
        content_type = self._get_content_type(file_extension)
        blob.content_type = content_type

        # Upload file
        file.file.seek(0)
        blob.upload_from_file(file.file, content_type=content_type)

        # Make blob publicly readable (optional - depends on your security requirements)
        # blob.make_public()

        # Return the public URL or signed URL
        return f"gs://{bucket_name}/{storage_path}"

    def upload_photo(self, file: UploadFile, survey_slug: str, file_id: str) -> str:
        """
        Upload a photo file to the photos bucket
        """
        # Validate it's an image
        if not self._is_image_file(file.filename):
            raise ValueError("File must be an image")

        if not self.enabled:
            print(f"📷 Simulating photo upload: {file.filename}")

        # Process image if needed (resize, optimize)
        processed_file = self._process_image(file)

        return self._upload_to_bucket(processed_file, survey_slug, file_id, self.photo_bucket, self.photo_bucket_name)

    def upload_video(self, file: UploadFile, survey_slug: str, file_id: str) -> tuple[str, Optional[str]]:
        """
        Upload a video file to the videos bucket
        Returns (video_url, thumbnail_url)
        """
        # Validate it's a video file
        if not self._is_video_file(file.filename):
            raise ValueError("File must be a video")

        if not self.enabled:
            print(f"🎥 Simulating video upload: {file.filename}")

        # Upload video to videos bucket
        video_url = self._upload_to_bucket(file, survey_slug, file_id, self.video_bucket, self.video_bucket_name)

        # For now, return None for thumbnail - this can be implemented later
        # with video processing libraries like ffmpeg
        thumbnail_url = None

        return video_url, thumbnail_url

    def generate_signed_url(self, blob_path: str, expiration_hours: int = 24) -> str:
        """
        Generate a signed URL for accessing a file
        """
        blob = self.bucket.blob(blob_path)
        from datetime import timedelta
        url = blob.generate_signed_url(expiration=timedelta(hours=expiration_hours))
        return url

    def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from GCP Storage
        """
        try:
            blob = self.bucket.blob(storage_path)
            blob.delete()
            return True
        except Exception:
            return False

    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'mp4': 'video/mp4',
            'avi': 'video/avi',
            'mov': 'video/quicktime',
            'wmv': 'video/x-ms-wmv',
            'webm': 'video/webm'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')

    def _is_image_file(self, filename: str) -> bool:
        """Check if file is an image"""
        if not filename:
            return False
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        return any(filename.lower().endswith(ext) for ext in image_extensions)

    def _is_video_file(self, filename: str) -> bool:
        """Check if file is a video"""
        if not filename:
            return False
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv'}
        return any(filename.lower().endswith(ext) for ext in video_extensions)

    def _process_image(self, file: UploadFile) -> UploadFile:
        """
        Process image (resize, optimize) if needed
        For now, just return the original file
        """
        # Future: Add image processing logic here
        # - Resize large images
        # - Convert to web-friendly formats
        # - Compress images
        return file

# Global instance
gcp_storage = GCPStorageManager()

# Helper functions for external use
def upload_survey_photo(file: UploadFile, survey_slug: str) -> tuple[str, str]:
    """Upload photo and return (file_url, file_id)"""
    file_id = str(uuid.uuid4())
    file_url = gcp_storage.upload_photo(file, survey_slug, file_id)
    return file_url, file_id

def upload_survey_video(file: UploadFile, survey_slug: str) -> tuple[str, str, Optional[str]]:
    """Upload video and return (file_url, file_id, thumbnail_url)"""
    file_id = str(uuid.uuid4())
    file_url, thumbnail_url = gcp_storage.upload_video(file, survey_slug, file_id)
    return file_url, file_id, thumbnail_url