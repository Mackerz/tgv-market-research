"""JSON utility functions for safe parsing and handling"""
import json
import logging
from typing import Any, Optional, List

logger = logging.getLogger(__name__)


def safe_json_parse(json_str: Optional[str], default: Any = None) -> Any:
    """
    Safely parse JSON string with default fallback

    Args:
        json_str: JSON string to parse
        default: Default value to return if parsing fails (defaults to empty list)

    Returns:
        Parsed JSON object or default value
    """
    if not json_str:
        return default if default is not None else []

    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {json_str[:100]}... Error: {str(e)}")
        return default if default is not None else []


def safe_json_dumps(obj: Any, default: Optional[str] = None) -> Optional[str]:
    """
    Safely convert object to JSON string

    Args:
        obj: Object to convert to JSON
        default: Default value to return if conversion fails

    Returns:
        JSON string or default value
    """
    if obj is None:
        return default

    try:
        return json.dumps(obj)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {str(e)}")
        return default
