"""Input validation and sanitization utilities"""
import re
from typing import Optional
import bleach
from fastapi import UploadFile, HTTPException
from pydantic import validator
import magic


def sanitize_html(text: str) -> str:
    """
    Remove potentially dangerous HTML from user input.
    Uses bleach library to strip all HTML tags.

    Args:
        text: User input that may contain HTML

    Returns:
        Sanitized text with HTML removed
    """
    if not text:
        return text

    # Strip all HTML tags
    return bleach.clean(text, tags=[], strip=True)


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    if not email:
        return False

    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# Common disposable email domains to block
DISPOSABLE_EMAIL_DOMAINS = {
    'tempmail.com', 'temp-mail.org', '10minutemail.com', 'guerrillamail.com',
    'mailinator.com', 'throwaway.email', 'trashmail.com', 'sharklasers.com',
    'maildrop.cc', 'mailnesia.com', 'yopmail.com', 'getnada.com',
    'tempr.email', 'fakeinbox.com', 'mohmal.com', 'fakemail.net',
    'mintemail.com', 'mytemp.email', 'getairmail.com', 'temp-link.net',
    '10minemail.com', 'emailondeck.com', 'dispostable.com', 'guerrillamailblock.com',
    'spam4.me', 'grr.la', 'themostemail.com', 'emailfake.com',
}


def validate_email_extended(email: str, allow_disposable: bool = False) -> tuple[bool, Optional[str]]:
    """
    Extended email validation with disposable domain checking.

    Args:
        email: Email address to validate
        allow_disposable: If False, reject disposable email domains

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid
    """
    if not email:
        return (False, "Email is required")

    email = email.lower().strip()

    # Basic format validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return (False, "Invalid email format")

    # Check for obviously fake patterns
    local_part, domain = email.split('@')

    # Reject common test patterns
    if local_part in ['test', 'example', 'admin', 'no-reply', 'noreply']:
        return (False, "Email address appears to be a placeholder")

    # Check for disposable domains
    if not allow_disposable:
        if domain in DISPOSABLE_EMAIL_DOMAINS:
            return (False, "Disposable email addresses are not allowed. Please use a permanent email address.")

    # Check domain has at least one dot (basic TLD check)
    if '.' not in domain:
        return (False, "Invalid email domain")

    # Reject domains that look suspicious
    suspicious_patterns = ['test.com', 'example.com', 'localhost', '.local']
    if any(pattern in domain for pattern in suspicious_patterns):
        return (False, "Email address appears to be invalid")

    return (True, None)


def validate_email_for_pydantic(email: str) -> str:
    """
    Validate email for use in Pydantic schemas (raises ValueError on invalid).

    Args:
        email: Email address to validate

    Returns:
        Validated and normalized email (lowercase)

    Raises:
        ValueError: If email is invalid or disposable
    """
    is_valid, error_message = validate_email_extended(email, allow_disposable=False)
    if not is_valid:
        raise ValueError(error_message)
    return email.lower().strip()


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    Accepts formats: +1234567890, (123) 456-7890, 123-456-7890, etc.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid phone format, False otherwise
    """
    if not phone:
        return False

    # Remove common separators
    digits = re.sub(r'[+\-\(\)\s]', '', phone)

    # Check if only digits remain and length is reasonable (7-15 digits)
    return digits.isdigit() and 7 <= len(digits) <= 15


def validate_url(url: str, allowed_schemes: Optional[list] = None) -> bool:
    """
    Validate URL format and scheme.

    Args:
        url: URL to validate
        allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])

    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False

    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']

    # Basic URL pattern
    pattern = r'^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        return False

    # Check scheme
    scheme = url.split('://')[0].lower()
    return scheme in allowed_schemes


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and injection attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem operations
    """
    if not filename:
        return filename

    # Remove directory separators and null bytes
    filename = filename.replace('/', '').replace('\\', '').replace('\0', '')

    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')

    # Replace special characters with underscores
    filename = re.sub(r'[<>:"|?*]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]

    return filename


def validate_slug(slug: str) -> bool:
    """
    Validate slug format (lowercase letters, numbers, hyphens, underscores only).

    Args:
        slug: Slug to validate

    Returns:
        True if valid slug, False otherwise
    """
    if not slug:
        return False

    # Must start with letter or number, contain only letters, numbers, hyphens, underscores
    pattern = r'^[a-z0-9][a-z0-9\-_]*$'
    return bool(re.match(pattern, slug, re.IGNORECASE))


def truncate_text(text: str, max_length: int = 1000, suffix: str = '...') -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length (default: 1000)
        suffix: Suffix to add when truncated (default: '...')

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def validate_json_size(data: dict, max_size_kb: int = 100) -> bool:
    """
    Validate that JSON data doesn't exceed size limit.

    Args:
        data: Dictionary to validate
        max_size_kb: Maximum size in kilobytes (default: 100KB)

    Returns:
        True if within size limit, False otherwise
    """
    import json
    import sys

    try:
        json_str = json.dumps(data)
        size_bytes = sys.getsizeof(json_str)
        size_kb = size_bytes / 1024
        return size_kb <= max_size_kb
    except Exception:
        return False


def sanitize_user_input(text: str, max_length: int = 2000) -> str:
    """
    Comprehensive sanitization for user text input.
    Combines HTML sanitization and length limiting.

    Args:
        text: User input text
        max_length: Maximum allowed length (default: 2000)

    Returns:
        Sanitized and truncated text
    """
    if not text:
        return text

    # Remove HTML
    text = sanitize_html(text)

    # Truncate to max length
    text = truncate_text(text, max_length, suffix='')

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


# File Upload Validation

class FileValidator:
    """Comprehensive file upload validation"""

    # Size limits
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB

    # Allowed MIME types (using magic bytes verification)
    ALLOWED_IMAGE_MIMES = {
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/bmp'
    }

    ALLOWED_VIDEO_MIMES = {
        'video/mp4',
        'video/quicktime',
        'video/webm',
        'video/x-msvideo',  # AVI
        'video/x-ms-wmv'     # WMV
    }

    # Allowed file extensions (as additional check)
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.webm', '.avi', '.wmv'}

    @staticmethod
    async def validate_image(file: UploadFile) -> UploadFile:
        """
        Validate image upload with comprehensive checks.

        Args:
            file: Uploaded file

        Returns:
            The same file if validation passes

        Raises:
            HTTPException: If validation fails
        """
        # Read file contents
        contents = await file.read()
        file_size = len(contents)

        # Check file size
        if file_size > FileValidator.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Maximum size is {FileValidator.MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Check file extension
        if file.filename:
            extension = '.' + file.filename.split('.')[-1].lower()
            if extension not in FileValidator.ALLOWED_IMAGE_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image file extension. Allowed: {', '.join(FileValidator.ALLOWED_IMAGE_EXTENSIONS)}"
                )

        # Verify MIME type using magic bytes (content-based detection)
        try:
            mime_type = magic.from_buffer(contents, mime=True)
            if mime_type not in FileValidator.ALLOWED_IMAGE_MIMES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image type: {mime_type}. The file content does not match an allowed image format."
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not determine file type: {str(e)}"
            )

        # Reset file pointer for subsequent reads
        await file.seek(0)

        return file

    @staticmethod
    async def validate_video(file: UploadFile) -> UploadFile:
        """
        Validate video upload with comprehensive checks.

        Args:
            file: Uploaded file

        Returns:
            The same file if validation passes

        Raises:
            HTTPException: If validation fails
        """
        # Read file contents
        contents = await file.read()
        file_size = len(contents)

        # Check file size
        if file_size > FileValidator.MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Video too large. Maximum size is {FileValidator.MAX_VIDEO_SIZE / 1024 / 1024:.0f}MB"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Check file extension
        if file.filename:
            extension = '.' + file.filename.split('.')[-1].lower()
            if extension not in FileValidator.ALLOWED_VIDEO_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid video file extension. Allowed: {', '.join(FileValidator.ALLOWED_VIDEO_EXTENSIONS)}"
                )

        # Verify MIME type using magic bytes (content-based detection)
        try:
            mime_type = magic.from_buffer(contents, mime=True)
            if mime_type not in FileValidator.ALLOWED_VIDEO_MIMES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid video type: {mime_type}. The file content does not match an allowed video format."
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not determine file type: {str(e)}"
            )

        # Reset file pointer for subsequent reads
        await file.seek(0)

        return file

    @staticmethod
    def is_image_extension(filename: str) -> bool:
        """Check if filename has image extension"""
        if not filename:
            return False
        extension = '.' + filename.split('.')[-1].lower()
        return extension in FileValidator.ALLOWED_IMAGE_EXTENSIONS

    @staticmethod
    def is_video_extension(filename: str) -> bool:
        """Check if filename has video extension"""
        if not filename:
            return False
        extension = '.' + filename.split('.')[-1].lower()
        return extension in FileValidator.ALLOWED_VIDEO_EXTENSIONS
