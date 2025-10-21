"""Tests for validation utilities including file upload validation"""
import pytest
from io import BytesIO
from fastapi import UploadFile, HTTPException

from app.utils.validation import (
    FileValidator,
    validate_email_extended,
    validate_email_for_pydantic,
    sanitize_user_input,
    sanitize_html,
    DISPOSABLE_EMAIL_DOMAINS
)


class TestFileValidator:
    """Tests for FileValidator class"""

    @pytest.mark.asyncio
    async def test_validate_image_valid_jpeg(self):
        """Test validating a valid JPEG image"""
        # Create a minimal valid JPEG (magic bytes: FF D8 FF)
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
        file = UploadFile(
            filename="test.jpg",
            file=BytesIO(jpeg_data)
        )
        
        result = await FileValidator.validate_image(file)
        assert result is not None
        assert result.filename == "test.jpg"

    @pytest.mark.asyncio
    async def test_validate_image_valid_png(self):
        """Test validating a valid PNG image"""
        # More complete PNG header with IHDR chunk
        # PNG signature + IHDR chunk
        png_data = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR'  # IHDR chunk length and type
            b'\x00\x00\x00\x01'  # Width: 1
            b'\x00\x00\x00\x01'  # Height: 1
            b'\x08\x02\x00\x00\x00'  # Bit depth, color type, etc.
            b'\x90wS\xde'  # CRC
            b'\x00\x00\x00\x00IEND\xaeB`\x82'  # IEND chunk
        )
        file = UploadFile(
            filename="test.png",
            file=BytesIO(png_data)
        )

        result = await FileValidator.validate_image(file)
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_image_too_large(self):
        """Test rejection of oversized images"""
        # Create file larger than 10MB
        large_data = b'\xff\xd8\xff\xe0' + b'\x00' * (11 * 1024 * 1024)
        file = UploadFile(
            filename="large.jpg",
            file=BytesIO(large_data)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_image(file)
        assert exc_info.value.status_code == 400
        assert "too large" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_validate_image_empty_file(self):
        """Test rejection of empty files"""
        file = UploadFile(
            filename="empty.jpg",
            file=BytesIO(b'')
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_image(file)
        assert exc_info.value.status_code == 400
        assert "empty" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_validate_image_wrong_extension(self):
        """Test rejection of wrong file extension"""
        jpeg_data = b'\xff\xd8\xff\xe0' + b'\x00' * 100
        file = UploadFile(
            filename="test.exe",
            file=BytesIO(jpeg_data)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_image(file)
        assert exc_info.value.status_code == 400
        assert "extension" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_validate_image_fake_extension(self):
        """Test rejection of file with image extension but wrong content"""
        # Create a file with .jpg extension but text content
        text_data = b'This is not an image file'
        file = UploadFile(
            filename="fake.jpg",
            file=BytesIO(text_data)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_image(file)
        assert exc_info.value.status_code == 400
        assert "invalid" in exc_info.value.detail.lower() or "type" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_validate_video_valid_mp4(self):
        """Test validating a valid MP4 video"""
        # MP4 magic bytes: starts with ftyp
        mp4_data = b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 1000
        file = UploadFile(
            filename="test.mp4",
            file=BytesIO(mp4_data)
        )
        
        result = await FileValidator.validate_video(file)
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_video_too_large(self):
        """Test rejection of oversized videos"""
        # Create file larger than 100MB
        large_data = b'\x00\x00\x00\x18ftypmp42' + b'\x00' * (101 * 1024 * 1024)
        file = UploadFile(
            filename="large.mp4",
            file=BytesIO(large_data)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_video(file)
        assert exc_info.value.status_code == 400
        assert "too large" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_validate_video_wrong_extension(self):
        """Test rejection of wrong video extension"""
        mp4_data = b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 1000
        file = UploadFile(
            filename="test.jpg",
            file=BytesIO(mp4_data)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_video(file)
        assert exc_info.value.status_code == 400

    def test_is_image_extension_valid(self):
        """Test image extension detection"""
        assert FileValidator.is_image_extension("photo.jpg") is True
        assert FileValidator.is_image_extension("photo.jpeg") is True
        assert FileValidator.is_image_extension("photo.png") is True
        assert FileValidator.is_image_extension("photo.gif") is True
        assert FileValidator.is_image_extension("photo.webp") is True
        
    def test_is_image_extension_invalid(self):
        """Test rejection of non-image extensions"""
        assert FileValidator.is_image_extension("video.mp4") is False
        assert FileValidator.is_image_extension("document.pdf") is False
        assert FileValidator.is_image_extension("script.exe") is False
        assert FileValidator.is_image_extension(None) is False
        assert FileValidator.is_image_extension("") is False

    def test_is_video_extension_valid(self):
        """Test video extension detection"""
        assert FileValidator.is_video_extension("video.mp4") is True
        assert FileValidator.is_video_extension("video.mov") is True
        assert FileValidator.is_video_extension("video.webm") is True
        assert FileValidator.is_video_extension("video.avi") is True
        
    def test_is_video_extension_invalid(self):
        """Test rejection of non-video extensions"""
        assert FileValidator.is_video_extension("photo.jpg") is False
        assert FileValidator.is_video_extension("document.pdf") is False
        assert FileValidator.is_video_extension(None) is False


class TestEmailValidation:
    """Tests for enhanced email validation"""

    def test_validate_email_extended_valid(self):
        """Test validation of valid emails"""
        valid, error = validate_email_extended("user@company.com")
        assert valid is True
        assert error is None

        valid, error = validate_email_extended("john.doe+tag@company.co.uk")
        assert valid is True
        assert error is None

    def test_validate_email_extended_disposable(self):
        """Test rejection of disposable email domains"""
        for domain in ['tempmail.com', '10minutemail.com', 'guerrillamail.com']:
            # Use non-placeholder email addresses
            valid, error = validate_email_extended(f"user123@{domain}")
            assert valid is False
            assert "disposable" in error.lower()

    def test_validate_email_extended_allow_disposable(self):
        """Test allowing disposable emails when flag is set"""
        # Use a non-placeholder email with disposable domain
        valid, error = validate_email_extended("user123@tempmail.com", allow_disposable=True)
        assert valid is True
        assert error is None

    def test_validate_email_extended_placeholder(self):
        """Test rejection of placeholder emails"""
        placeholders = ['test@example.com', 'admin@example.com', 'no-reply@example.com']
        for email in placeholders:
            valid, error = validate_email_extended(email)
            assert valid is False
            assert "placeholder" in error.lower() or "invalid" in error.lower()

    def test_validate_email_extended_invalid_format(self):
        """Test rejection of invalid email formats"""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user@.com',
            'user..name@example.com',
            ''
        ]
        for email in invalid_emails:
            valid, error = validate_email_extended(email)
            assert valid is False
            assert error is not None

    def test_validate_email_extended_suspicious_domains(self):
        """Test rejection of suspicious domains"""
        suspicious = ['user@test.com', 'user@localhost', 'user@example.com']
        for email in suspicious:
            valid, error = validate_email_extended(email)
            assert valid is False

    def test_validate_email_for_pydantic_valid(self):
        """Test Pydantic validator with valid email"""
        result = validate_email_for_pydantic("User@Company.COM")
        assert result == "user@company.com"  # Should be normalized to lowercase

    def test_validate_email_for_pydantic_invalid(self):
        """Test Pydantic validator raises ValueError for invalid email"""
        with pytest.raises(ValueError) as exc_info:
            validate_email_for_pydantic("user123@tempmail.com")
        assert "disposable" in str(exc_info.value).lower()

    def test_disposable_domains_list_not_empty(self):
        """Ensure disposable domains list is populated"""
        assert len(DISPOSABLE_EMAIL_DOMAINS) > 20
        assert 'tempmail.com' in DISPOSABLE_EMAIL_DOMAINS
        assert 'guerrillamail.com' in DISPOSABLE_EMAIL_DOMAINS


class TestInputSanitization:
    """Tests for input sanitization"""

    def test_sanitize_html_removes_script_tags(self):
        """Test removal of script tags"""
        dirty = "<script>alert('XSS')</script>Hello"
        clean = sanitize_html(dirty)
        assert "<script>" not in clean
        assert "</script>" not in clean
        # bleach.clean removes tags but keeps text content between tags
        assert "alert('XSS')Hello" in clean or "Hello" in clean

    def test_sanitize_html_removes_img_tags(self):
        """Test removal of image tags"""
        dirty = '<img src=x onerror=alert(1)>Text'
        clean = sanitize_html(dirty)
        assert "<img" not in clean
        assert "onerror" not in clean
        assert "Text" in clean

    def test_sanitize_html_removes_links(self):
        """Test removal of link tags"""
        dirty = '<a href="http://malicious.com">Click me</a>'
        clean = sanitize_html(dirty)
        assert "<a" not in clean
        assert "href" not in clean
        assert "Click me" in clean

    def test_sanitize_html_removes_styles(self):
        """Test removal of style tags"""
        dirty = '<style>body{display:none}</style>Content'
        clean = sanitize_html(dirty)
        assert "<style>" not in clean
        assert "</style>" not in clean
        # bleach.clean removes tags but keeps text content
        assert "Content" in clean

    def test_sanitize_html_empty_input(self):
        """Test sanitization of empty/None input"""
        assert sanitize_html("") == ""
        assert sanitize_html(None) is None

    def test_sanitize_user_input_full_pipeline(self):
        """Test full sanitization pipeline"""
        dirty = "<script>alert('XSS')</script>  Valid text here  "
        clean = sanitize_user_input(dirty, max_length=100)

        # Should remove HTML tags
        assert "<script>" not in clean
        assert "</script>" not in clean

        # Should keep valid text
        assert "Valid text here" in clean

        # Should strip leading/trailing whitespace
        assert not clean.startswith(" ")
        assert not clean.endswith(" ")

    def test_sanitize_user_input_truncates_long_text(self):
        """Test truncation of long inputs"""
        long_text = "A" * 3000
        clean = sanitize_user_input(long_text, max_length=2000)
        assert len(clean) == 2000

    def test_sanitize_user_input_preserves_short_text(self):
        """Test that short text is preserved"""
        short_text = "This is a normal response"
        clean = sanitize_user_input(short_text, max_length=2000)
        assert clean == short_text

    def test_sanitize_user_input_handles_unicode(self):
        """Test handling of unicode characters"""
        unicode_text = "Hello 世界 🌍"
        clean = sanitize_user_input(unicode_text)
        assert "Hello" in clean
        assert "世界" in clean
        assert "🌍" in clean


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
