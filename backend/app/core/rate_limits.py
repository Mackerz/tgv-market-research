"""
Rate Limiting Configuration

Defines rate limits for different endpoint categories to prevent abuse
and control costs (especially for GCP AI API calls).
"""

# Default rate limit for most endpoints
DEFAULT_RATE_LIMIT = "100/minute"

# Stricter limits for expensive or sensitive operations
RATE_LIMITS = {
    # File uploads - cost storage and bandwidth
    "file_upload": "20/minute",  # Max 20 file uploads per minute per IP

    # Survey creation - prevent spam
    "survey_create": "10/minute",  # Max 10 surveys per minute per IP

    # AI analysis triggers - VERY expensive (GCP API costs)
    "ai_analysis": "5/minute",  # Max 5 AI analysis requests per minute

    # Submission creation - moderate
    "submission_create": "30/minute",  # Max 30 submissions per minute

    # Response creation - moderate
    "response_create": "50/minute",  # Max 50 responses per minute

    # Report/analytics - database intensive
    "reporting": "30/minute",  # Max 30 report requests per minute

    # Read operations - less strict
    "read_operations": "200/minute",  # Max 200 read requests per minute
}


def get_rate_limit(category: str) -> str:
    """
    Get rate limit for a specific category.

    Args:
        category: Rate limit category (e.g., 'file_upload', 'ai_analysis')

    Returns:
        Rate limit string (e.g., '20/minute')
    """
    return RATE_LIMITS.get(category, DEFAULT_RATE_LIMIT)
