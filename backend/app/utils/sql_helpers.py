"""SQL Helper Functions"""


def escape_like_pattern(pattern: str) -> str:
    """
    Escape special characters in LIKE/ILIKE patterns to prevent SQL injection.

    Escapes the following characters:
    - Backslash (\) -> \\\\
    - Percent (%) -> \\%
    - Underscore (_) -> \\_

    Args:
        pattern: The search pattern to escape

    Returns:
        Escaped pattern safe for use in LIKE/ILIKE queries

    Example:
        >>> escape_like_pattern("test%value")
        'test\\%value'
        >>> escape_like_pattern("test_value")
        'test\\_value'
    """
    if not pattern:
        return pattern

    # Escape backslash first, then other special characters
    pattern = pattern.replace('\\', '\\\\')
    pattern = pattern.replace('%', '\\%')
    pattern = pattern.replace('_', '\\_')

    return pattern
