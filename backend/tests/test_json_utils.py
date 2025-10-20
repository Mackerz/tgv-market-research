"""Unit tests for JSON utilities"""
import pytest
import json
from app.utils.json import


class TestSafeJsonParse:
    """Tests for safe_json_parse function"""

    def test_parse_valid_json_array(self):
        """Should parse valid JSON array"""
        json_str = '["item1", "item2", "item3"]'
        result = safe_json_parse(json_str)
        assert result == ["item1", "item2", "item3"]

    def test_parse_valid_json_object(self):
        """Should parse valid JSON object"""
        json_str = '{"key": "value", "number": 42}'
        result = safe_json_parse(json_str)
        assert result == {"key": "value", "number": 42}

    def test_parse_empty_string(self):
        """Should return default for empty string"""
        result = safe_json_parse("")
        assert result == []

    def test_parse_none(self):
        """Should return default for None"""
        result = safe_json_parse(None)
        assert result == []

    def test_parse_invalid_json(self):
        """Should return default for invalid JSON"""
        json_str = '{"invalid": json}'
        result = safe_json_parse(json_str, default=[])
        assert result == []

    def test_parse_with_custom_default(self):
        """Should use custom default when parsing fails"""
        json_str = "invalid"
        result = safe_json_parse(json_str, default={"error": True})
        assert result == {"error": True}

    def test_parse_malformed_json(self):
        """Should handle malformed JSON gracefully"""
        json_str = '["unclosed array"'
        result = safe_json_parse(json_str, default=[])
        assert result == []

    def test_parse_json_with_special_characters(self):
        """Should parse JSON with special characters"""
        json_str = '["item with \\"quotes\\"", "item with \\n newline"]'
        result = safe_json_parse(json_str)
        assert len(result) == 2
        assert 'quotes' in result[0]

    def test_parse_nested_json(self):
        """Should parse nested JSON structures"""
        json_str = '{"outer": {"inner": ["value1", "value2"]}}'
        result = safe_json_parse(json_str)
        assert result["outer"]["inner"] == ["value1", "value2"]

    def test_parse_json_number_types(self):
        """Should preserve number types in JSON"""
        json_str = '{"int": 42, "float": 3.14, "bool": true, "null": null}'
        result = safe_json_parse(json_str)
        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["bool"] is True
        assert result["null"] is None


class TestSafeJsonDumps:
    """Tests for safe_json_dumps function"""

    def test_dumps_list(self):
        """Should convert list to JSON string"""
        data = ["item1", "item2", "item3"]
        result = safe_json_dumps(data)
        assert result == '["item1", "item2", "item3"]'

    def test_dumps_dict(self):
        """Should convert dict to JSON string"""
        data = {"key": "value", "number": 42}
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_none(self):
        """Should return None for None input"""
        result = safe_json_dumps(None)
        assert result is None

    def test_dumps_with_custom_default(self):
        """Should use custom default when conversion fails"""
        # Create an object that can't be serialized
        class NonSerializable:
            pass

        obj = NonSerializable()
        result = safe_json_dumps(obj, default="error")
        assert result == "error"

    def test_dumps_empty_list(self):
        """Should handle empty list"""
        result = safe_json_dumps([])
        assert result == "[]"

    def test_dumps_empty_dict(self):
        """Should handle empty dict"""
        result = safe_json_dumps({})
        assert result == "{}"

    def test_dumps_nested_structure(self):
        """Should handle nested structures"""
        data = {
            "level1": {
                "level2": ["a", "b", "c"],
                "number": 42
            }
        }
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_preserves_types(self):
        """Should preserve data types"""
        data = {
            "string": "text",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3]
        }
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        assert parsed == data


class TestJsonUtilsIntegration:
    """Integration tests for JSON utilities"""

    def test_roundtrip_conversion(self):
        """Should successfully roundtrip data through dumps and parse"""
        original_data = {
            "labels": ["label1", "label2", "label3"],
            "brands": ["Brand A", "Brand B"],
            "metadata": {"count": 5, "valid": True}
        }

        # Convert to JSON
        json_str = safe_json_dumps(original_data)
        assert json_str is not None

        # Parse back
        parsed_data = safe_json_parse(json_str)
        assert parsed_data == original_data

    def test_handles_database_scenario(self):
        """Should handle typical database read/write scenario"""
        # Simulate writing to database
        labels = ["positive_sentiment", "product_interaction", "home_environment"]
        stored_json = safe_json_dumps(labels)

        # Simulate reading from database
        retrieved_labels = safe_json_parse(stored_json, [])
        assert retrieved_labels == labels

    def test_handles_null_database_field(self):
        """Should handle null database fields gracefully"""
        # Simulate reading null field from database
        db_value = None
        result = safe_json_parse(db_value, [])
        assert result == []

    def test_handles_corrupted_database_data(self):
        """Should handle corrupted data from database"""
        # Simulate corrupted JSON in database
        corrupted = '["incomplete'
        result = safe_json_parse(corrupted, [])
        assert result == []
