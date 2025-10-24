"""Unit tests for Gemini AI integration"""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch

from app.integrations.gcp.gemini import (
    GeminiLabelGenerator,
    generate_labels_for_media
)


@pytest.fixture
def gemini_disabled():
    """Create GeminiLabelGenerator with disabled state"""
    with patch.dict('os.environ', {'GEMINI_ENABLED': 'false'}):
        generator = GeminiLabelGenerator()
        return generator


@pytest.fixture
def gemini_with_mock_model():
    """Create GeminiLabelGenerator with mocked model"""
    with patch.dict('os.environ', {'GEMINI_ENABLED': 'true', 'GEMINI_API_KEY': 'test-key'}):
        with patch('app.integrations.gcp.gemini.genai'):
            with patch('app.integrations.gcp.gemini.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model_class.return_value = mock_model
                generator = GeminiLabelGenerator()
                generator.model = mock_model
                generator.enabled = True
                return generator, mock_model


class TestGeminiInitialization:
    """Tests for GeminiLabelGenerator initialization"""

    def test_initialization_disabled(self):
        """Test initialization when Gemini is disabled"""
        with patch.dict('os.environ', {'GEMINI_ENABLED': 'false'}):
            generator = GeminiLabelGenerator()
            assert generator.enabled is False

    @patch('app.integrations.gcp.gemini.genai')
    def test_initialization_with_api_key(self, mock_genai):
        """Test initialization with API key"""
        with patch.dict('os.environ', {'GEMINI_ENABLED': 'true', 'GEMINI_API_KEY': 'test-key'}):
            generator = GeminiLabelGenerator()
            mock_genai.configure.assert_called_once_with(api_key='test-key')

    @patch('app.integrations.gcp.gemini.genai')
    def test_initialization_fallback_on_error(self, mock_genai):
        """Test initialization falls back to disabled on error"""
        mock_genai.GenerativeModel.side_effect = Exception("API error")
        with patch.dict('os.environ', {'GEMINI_ENABLED': 'true', 'GEMINI_API_KEY': 'test-key'}):
            generator = GeminiLabelGenerator()
            assert generator.enabled is False
            assert generator.model is None


class TestGenerateReportingLabels:
    """Tests for generate_reporting_labels method"""

    def test_generate_labels_disabled_mode(self, gemini_disabled):
        """Test label generation in disabled mode returns simulated labels"""
        labels = gemini_disabled.generate_reporting_labels("A can of Monster Energy")

        assert isinstance(labels, list)
        assert len(labels) > 0
        assert all(isinstance(label, str) for label in labels)
        assert "product_interaction" in labels

    def test_generate_labels_success(self, gemini_with_mock_model):
        """Test successful label generation with Gemini"""
        generator, mock_model = gemini_with_mock_model

        mock_response = MagicMock()
        mock_response.text = '["beverage_consumption", "energy_drink", "aluminum_can", "brand_awareness", "positive_sentiment"]'
        mock_model.generate_content.return_value = mock_response

        labels = generator.generate_reporting_labels(
            description="A can of Monster Energy drink on a table",
            transcript="I love Monster Energy",
            brands=["Monster Energy"]
        )

        assert labels == ["beverage_consumption", "energy_drink", "aluminum_can", "brand_awareness", "positive_sentiment"]
        mock_model.generate_content.assert_called_once()

    def test_generate_labels_with_description_only(self, gemini_with_mock_model):
        """Test label generation with description only"""
        generator, mock_model = gemini_with_mock_model

        mock_response = MagicMock()
        mock_response.text = '["label1", "label2"]'
        mock_model.generate_content.return_value = mock_response

        labels = generator.generate_reporting_labels(description="Test description")

        assert labels is not None
        assert len(labels) == 2

    def test_generate_labels_json_parse_error(self, gemini_with_mock_model):
        """Test label generation handles invalid JSON"""
        generator, mock_model = gemini_with_mock_model

        mock_response = MagicMock()
        mock_response.text = 'This is not JSON'
        mock_model.generate_content.return_value = mock_response

        labels = generator.generate_reporting_labels(description="Test")

        assert labels is None

    def test_generate_labels_extracts_json_from_text(self, gemini_with_mock_model):
        """Test label generation extracts JSON from surrounding text"""
        generator, mock_model = gemini_with_mock_model

        mock_response = MagicMock()
        mock_response.text = 'Here are the labels: ["label1", "label2", "label3"] based on the analysis'
        mock_model.generate_content.return_value = mock_response

        labels = generator.generate_reporting_labels(description="Test")

        assert labels == ["label1", "label2", "label3"]

    def test_generate_labels_exception_handling(self, gemini_with_mock_model):
        """Test label generation handles API exceptions"""
        generator, mock_model = gemini_with_mock_model

        mock_model.generate_content.side_effect = Exception("API error")

        labels = generator.generate_reporting_labels(description="Test")

        assert labels is None


class TestGetLabelSummary:
    """Tests for get_label_summary method"""

    def test_label_summary_empty_input(self, gemini_disabled):
        """Test label summary with empty input"""
        summary = gemini_disabled.get_label_summary([])

        assert summary == {}

    def test_label_summary_counts_labels(self, gemini_disabled):
        """Test label summary counts label frequencies"""
        all_labels = [
            ["label1", "label2", "label3"],
            ["label1", "label2"],
            ["label1", "label4"]
        ]

        summary = gemini_disabled.get_label_summary(all_labels)

        assert summary["label1"] == 3
        assert summary["label2"] == 2
        assert summary["label3"] == 1
        assert summary["label4"] == 1

    def test_label_summary_sorted_by_frequency(self, gemini_disabled):
        """Test label summary is sorted by frequency"""
        all_labels = [
            ["rare"],
            ["common", "common", "common"],
            ["common", "medium", "medium"]
        ]

        summary = gemini_disabled.get_label_summary(all_labels)
        keys = list(summary.keys())

        # Most frequent should be first
        assert keys[0] == "common"

    def test_label_summary_handles_none(self, gemini_disabled):
        """Test label summary handles None values"""
        all_labels = [
            ["label1"],
            None,
            ["label2"]
        ]

        summary = gemini_disabled.get_label_summary(all_labels)

        assert summary["label1"] == 1
        assert summary["label2"] == 1


class TestSummarizeLabels:
    """Tests for summarize_labels method"""

    def test_summarize_labels_disabled_mode(self, gemini_disabled):
        """Test label summarization in disabled mode"""
        labels = ["label1", "label2", "label3"]

        result = gemini_disabled.summarize_labels(labels)

        assert isinstance(result, dict)
        assert "themes" in result
        assert "insights" in result
        assert isinstance(result["themes"], list)
        assert isinstance(result["insights"], list)

    def test_summarize_labels_success(self, gemini_with_mock_model):
        """Test successful label summarization"""
        generator, mock_model = gemini_with_mock_model

        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "themes": [
                {
                    "theme": "Product Engagement",
                    "frequency": 10,
                    "consolidated_labels": ["product_interaction", "usage"],
                    "description": "Consumer engagement with products"
                }
            ],
            "insights": ["High product engagement"]
        })
        mock_model.generate_content.return_value = mock_response

        result = generator.summarize_labels(["label1", "label2", "label3"])

        assert "themes" in result
        assert len(result["themes"]) == 1
        assert result["themes"][0]["theme"] == "Product Engagement"

    def test_summarize_labels_exception_handling(self, gemini_with_mock_model):
        """Test label summarization handles exceptions"""
        generator, mock_model = gemini_with_mock_model

        mock_model.generate_content.side_effect = Exception("API error")

        result = generator.summarize_labels(["label1"])

        assert result == {"themes": [], "insights": []}


class TestGenerateTaxonomyCategories:
    """Tests for generate_taxonomy_categories method"""

    def test_taxonomy_disabled_mode(self, gemini_disabled):
        """Test taxonomy generation in disabled mode"""
        labels = ["label1", "label2", "label3"]

        result = gemini_disabled.generate_taxonomy_categories(labels, max_categories=4)

        assert isinstance(result, dict)
        assert "categories" in result
        assert isinstance(result["categories"], list)
        assert len(result["categories"]) > 0

    def test_taxonomy_success(self, gemini_with_mock_model):
        """Test successful taxonomy generation"""
        generator, mock_model = gemini_with_mock_model

        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "categories": [
                {
                    "category_name": "Consumer Behavior",
                    "description": "How consumers interact with products",
                    "system_labels": ["product_usage", "interaction"]
                }
            ]
        })
        mock_model.generate_content.return_value = mock_response

        result = generator.generate_taxonomy_categories(["label1", "label2"], max_categories=5)

        assert "categories" in result
        assert len(result["categories"]) == 1
        assert result["categories"][0]["category_name"] == "Consumer Behavior"

    def test_taxonomy_exception_handling(self, gemini_with_mock_model):
        """Test taxonomy generation handles exceptions"""
        generator, mock_model = gemini_with_mock_model

        mock_model.generate_content.side_effect = Exception("API error")

        result = generator.generate_taxonomy_categories(["label1"])

        assert result == {"categories": []}


class TestConvenienceFunction:
    """Tests for generate_labels_for_media convenience function"""

    @patch('app.integrations.gcp.gemini.gemini_labeler')
    def test_generate_labels_for_media(self, mock_labeler):
        """Test convenience function calls the labeler"""
        mock_labeler.generate_reporting_labels.return_value = ["label1", "label2"]

        result = generate_labels_for_media(
            description="Test description",
            transcript="Test transcript",
            brands=["Brand A"]
        )

        mock_labeler.generate_reporting_labels.assert_called_once_with(
            "Test description",
            "Test transcript",
            ["Brand A"]
        )
        assert result == ["label1", "label2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
