"""
Application-wide constants and configuration values.

This module centralizes magic numbers, limits, and other constants
used throughout the application for easier maintenance and configuration.
"""

# =============================================================================
# PAGINATION CONSTANTS
# =============================================================================

DEFAULT_PAGE_SIZE = 100
"""Default number of items per page for paginated API responses"""

MAX_PAGE_SIZE = 1000
"""Maximum allowed page size to prevent performance issues"""

# =============================================================================
# RATE LIMITING CONSTANTS
# =============================================================================

# Authentication
LOGIN_RATE_LIMIT = "5/minute"
"""Rate limit for login attempts (prevents brute force attacks)"""

GOOGLE_LOGIN_RATE_LIMIT = "10/minute"
"""Rate limit for Google OAuth login attempts"""

# Survey Operations
SURVEY_CREATE_RATE_LIMIT = "10/minute"
"""Rate limit for survey creation (admin operation)"""

SURVEY_UPLOAD_PHOTO_RATE_LIMIT = "30/minute"
"""Rate limit for photo uploads per IP"""

SURVEY_UPLOAD_VIDEO_RATE_LIMIT = "10/minute"
"""Rate limit for video uploads per IP (more resource-intensive)"""

# Reporting Operations
REPORTING_SUBMISSIONS_RATE_LIMIT = "60/minute"
"""Rate limit for fetching submission lists (prevent data scraping)"""

REPORTING_DATA_RATE_LIMIT = "30/minute"
"""Rate limit for fetching reporting analytics data"""

MEDIA_GALLERY_RATE_LIMIT = "60/minute"
"""Rate limit for media gallery endpoint"""

# Default rate limit for all other endpoints
DEFAULT_RATE_LIMIT = "100/minute"
"""Default rate limit applied to all endpoints unless specified"""

# =============================================================================
# FILE UPLOAD CONSTANTS
# =============================================================================

MAX_UPLOAD_SIZE_MB = 50
"""Maximum file size for media uploads in megabytes"""

MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
"""Maximum file size for media uploads in bytes"""

MAX_REQUEST_SIZE_MB = 10
"""Maximum request body size for non-upload endpoints in megabytes"""

MAX_REQUEST_SIZE_BYTES = MAX_REQUEST_SIZE_MB * 1024 * 1024
"""Maximum request body size for non-upload endpoints in bytes"""

# =============================================================================
# MEDIA & PREVIEW CONSTANTS
# =============================================================================

DEFAULT_MEDIA_PREVIEW_LIMIT = 5
"""Default number of media items to show in previews"""

MAX_MEDIA_PREVIEW_LIMIT = 20
"""Maximum number of media items allowed in preview requests"""

# =============================================================================
# TOKEN & SESSION CONSTANTS
# =============================================================================

ACCESS_TOKEN_EXPIRE_MINUTES = 30
"""Access token expiration time in minutes"""

REFRESH_TOKEN_EXPIRE_DAYS = 7
"""Refresh token expiration time in days"""

COOKIE_MAX_AGE_DAYS = 7
"""HTTP-only cookie max age in days"""

COOKIE_MAX_AGE_SECONDS = COOKIE_MAX_AGE_DAYS * 24 * 60 * 60
"""HTTP-only cookie max age in seconds"""

# =============================================================================
# TAXONOMY & AI CONSTANTS
# =============================================================================

DEFAULT_TAXONOMY_CATEGORIES = 6
"""Default number of high-level categories for AI taxonomy generation"""

MAX_TAXONOMY_CATEGORIES = 20
"""Maximum number of taxonomy categories allowed"""

# =============================================================================
# DATABASE QUERY CONSTANTS
# =============================================================================

DEFAULT_QUERY_TIMEOUT_SECONDS = 30
"""Default timeout for database queries in seconds"""

REPORTING_QUERY_TIMEOUT_SECONDS = 60
"""Timeout for complex reporting queries in seconds"""

# =============================================================================
# CACHE CONSTANTS
# =============================================================================

SURVEY_DATA_CACHE_SECONDS = 300
"""Cache duration for survey data (5 minutes)"""

REPORTING_DATA_CACHE_SECONDS = 60
"""Cache duration for reporting analytics (1 minute)"""

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

MIN_PASSWORD_LENGTH = 8
"""Minimum password length for user accounts"""

MAX_PASSWORD_LENGTH = 128
"""Maximum password length for user accounts"""

MIN_SURVEY_NAME_LENGTH = 3
"""Minimum survey name length"""

MAX_SURVEY_NAME_LENGTH = 200
"""Maximum survey name length"""

# =============================================================================
# HTTP HEADER CONSTANTS
# =============================================================================

HSTS_MAX_AGE_SECONDS = 31536000
"""HTTP Strict Transport Security max age (1 year in seconds)"""
