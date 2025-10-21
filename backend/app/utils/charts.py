"""Chart utilities for consistent color management"""
from typing import List


class ChartColorPalette:
    """Centralized chart color management for consistent visualization"""

    DEFAULT_COLORS = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
    ]

    GENDER_COLORS = ['#FF6384', '#36A2EB', '#FFCE56']

    @classmethod
    def get_colors(cls, count: int) -> List[str]:
        """
        Get color array for specified count

        Args:
            count: Number of colors needed

        Returns:
            List of color hex codes
        """
        # Handle edge cases
        if count <= 0:
            return []

        if count <= len(cls.DEFAULT_COLORS):
            return cls.DEFAULT_COLORS[:count]

        # If more colors needed, repeat the palette
        repeat_times = (count // len(cls.DEFAULT_COLORS)) + 1
        extended = cls.DEFAULT_COLORS * repeat_times
        return extended[:count]

    @classmethod
    def get_gender_colors(cls, count: int) -> List[str]:
        """Get colors specifically for gender charts"""
        return cls.GENDER_COLORS[:count]
