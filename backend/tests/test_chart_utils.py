"""Unit tests for chart utilities"""
import pytest
from app.utils.charts import


class TestChartColorPalette:
    """Tests for ChartColorPalette class"""

    def test_get_colors_basic(self):
        """Should return correct number of colors"""
        colors = ChartColorPalette.get_colors(5)
        assert len(colors) == 5
        assert all(color.startswith('#') for color in colors)

    def test_get_colors_zero(self):
        """Should handle zero count"""
        colors = ChartColorPalette.get_colors(0)
        assert len(colors) == 0
        assert colors == []

    def test_get_colors_one(self):
        """Should handle single color request"""
        colors = ChartColorPalette.get_colors(1)
        assert len(colors) == 1
        assert colors[0] == '#FF6384'

    def test_get_colors_max_palette_size(self):
        """Should return all colors when requesting full palette"""
        colors = ChartColorPalette.get_colors(10)
        assert len(colors) == 10
        assert colors == ChartColorPalette.DEFAULT_COLORS

    def test_get_colors_exceeds_palette(self):
        """Should repeat colors when count exceeds palette size"""
        count = 15  # More than default palette
        colors = ChartColorPalette.get_colors(count)
        assert len(colors) == count

        # First 10 should match default palette
        assert colors[:10] == ChartColorPalette.DEFAULT_COLORS
        # 11th color should be same as 1st (pattern repeats)
        assert colors[10] == colors[0]

    def test_get_colors_large_count(self):
        """Should handle large color counts"""
        colors = ChartColorPalette.get_colors(100)
        assert len(colors) == 100
        # Verify pattern repeats
        assert colors[0] == colors[10] == colors[20]

    def test_colors_are_hex_format(self):
        """Should return colors in hex format"""
        colors = ChartColorPalette.get_colors(5)
        for color in colors:
            assert color.startswith('#')
            assert len(color) == 7  # #RRGGBB format
            # Verify it's valid hex
            int(color[1:], 16)  # Should not raise exception

    def test_get_gender_colors(self):
        """Should return gender-specific colors"""
        colors = ChartColorPalette.get_gender_colors(3)
        assert len(colors) == 3
        assert colors == ChartColorPalette.GENDER_COLORS

    def test_get_gender_colors_partial(self):
        """Should return subset of gender colors"""
        colors = ChartColorPalette.get_gender_colors(2)
        assert len(colors) == 2
        assert colors == ChartColorPalette.GENDER_COLORS[:2]

    def test_default_colors_constant(self):
        """Should have expected default colors"""
        assert len(ChartColorPalette.DEFAULT_COLORS) == 10
        assert ChartColorPalette.DEFAULT_COLORS[0] == '#FF6384'
        assert ChartColorPalette.DEFAULT_COLORS[1] == '#36A2EB'
        assert ChartColorPalette.DEFAULT_COLORS[2] == '#FFCE56'

    def test_gender_colors_constant(self):
        """Should have expected gender colors"""
        assert len(ChartColorPalette.GENDER_COLORS) == 3
        assert ChartColorPalette.GENDER_COLORS[0] == '#FF6384'
        assert ChartColorPalette.GENDER_COLORS[1] == '#36A2EB'
        assert ChartColorPalette.GENDER_COLORS[2] == '#FFCE56'

    def test_colors_consistency(self):
        """Should return same colors for same count"""
        colors1 = ChartColorPalette.get_colors(5)
        colors2 = ChartColorPalette.get_colors(5)
        assert colors1 == colors2

    def test_class_method_behavior(self):
        """Should work as class method without instantiation"""
        # Should not need to create instance
        colors = ChartColorPalette.get_colors(3)
        assert len(colors) == 3

    def test_typical_chart_use_cases(self):
        """Should handle typical chart scenarios"""
        # Age ranges (5 categories)
        age_colors = ChartColorPalette.get_colors(5)
        assert len(age_colors) == 5

        # Regions (variable)
        region_colors = ChartColorPalette.get_colors(7)
        assert len(region_colors) == 7

        # Gender (2-3 categories)
        gender_colors = ChartColorPalette.get_gender_colors(2)
        assert len(gender_colors) == 2

    def test_integration_with_reporting(self):
        """Should work with reporting data structures"""
        # Simulate age range categories
        age_ranges = {
            "0-18": 10,
            "18-25": 25,
            "25-40": 30,
            "40-60": 20,
            "60+": 15
        }

        colors = ChartColorPalette.get_colors(len(age_ranges))
        assert len(colors) == len(age_ranges)

        # Can be used directly in chart data
        chart_data = {
            "labels": list(age_ranges.keys()),
            "data": list(age_ranges.values()),
            "backgroundColor": colors
        }
        assert len(chart_data["backgroundColor"]) == len(chart_data["labels"])


class TestChartColorPaletteEdgeCases:
    """Edge case tests for ChartColorPalette"""

    def test_negative_count(self):
        """Should handle negative count gracefully"""
        # Negative slice returns empty list in Python
        colors = ChartColorPalette.get_colors(-1)
        assert colors == []

    def test_very_large_count(self):
        """Should handle very large counts"""
        colors = ChartColorPalette.get_colors(1000)
        assert len(colors) == 1000

    def test_colors_immutability(self):
        """Modifying returned colors should not affect original palette"""
        colors = ChartColorPalette.get_colors(5)
        original_first_color = colors[0]

        # Try to modify returned list
        colors[0] = "#000000"

        # Get fresh colors
        new_colors = ChartColorPalette.get_colors(5)
        assert new_colors[0] == original_first_color
        assert new_colors[0] != "#000000"
