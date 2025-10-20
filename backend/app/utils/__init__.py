"""Utility functions for the application."""

from app.utils.charts import ChartColorPalette
from app.utils.json import safe_json_dumps, safe_json_parse
from app.utils.logging import ContextLogger, get_context_logger
from app.utils.queries import (
    get_approved_submission_ids_subquery,
    get_approved_submissions_query,
    get_completed_submissions_query,
    get_submission_counts,
)

__all__ = [
    # JSON utilities
    "safe_json_parse",
    "safe_json_dumps",
    # Logging utilities
    "ContextLogger",
    "get_context_logger",
    # Chart utilities
    "ChartColorPalette",
    # Query helpers
    "get_approved_submissions_query",
    "get_approved_submission_ids_subquery",
    "get_completed_submissions_query",
    "get_submission_counts",
]
