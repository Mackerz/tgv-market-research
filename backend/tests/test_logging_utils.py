"""Unit tests for logging utilities"""
import pytest
import logging
from app.utils.logging import ContextLogger, get_context_logger


class TestContextLogger:
    """Tests for ContextLogger class"""

    @pytest.fixture
    def logger(self):
        """Create a test logger"""
        return ContextLogger("test_logger")

    @pytest.fixture
    def log_capture(self, caplog):
        """Capture log output"""
        caplog.set_level(logging.INFO)
        return caplog

    def test_logger_initialization(self, logger):
        """Should initialize with logger name"""
        assert logger.logger is not None
        assert logger.logger.name == "test_logger"

    def test_info_start_basic(self, logger, log_capture):
        """Should log start message with emoji"""
        logger.info_start("operation")

        assert len(log_capture.records) == 1
        assert "🔄" in log_capture.text
        assert "Starting operation" in log_capture.text

    def test_info_start_with_context(self, logger, log_capture):
        """Should log start message with context"""
        logger.info_start("analysis", response_id=123, media_type="photo")

        assert "🔄" in log_capture.text
        assert "Starting analysis" in log_capture.text
        assert "response_id=123" in log_capture.text
        assert "media_type=photo" in log_capture.text

    def test_info_complete_basic(self, logger, log_capture):
        """Should log completion message"""
        logger.info_complete("operation")

        assert "✅" in log_capture.text
        assert "Completed operation" in log_capture.text

    def test_info_complete_with_result(self, logger, log_capture):
        """Should log completion with results"""
        logger.info_complete("analysis", result_id=456, success=True)

        assert "✅" in log_capture.text
        assert "Completed analysis" in log_capture.text
        assert "result_id=456" in log_capture.text
        assert "success=True" in log_capture.text

    def test_info_status(self, logger, log_capture):
        """Should log status message"""
        logger.info_status("processing data", records=100)

        assert "📋" in log_capture.text
        assert "processing data" in log_capture.text
        assert "records=100" in log_capture.text

    def test_warning(self, logger, log_capture):
        """Should log warning message"""
        logger.warning("potential issue", value=None)

        assert "⚠️" in log_capture.text
        assert "potential issue" in log_capture.text
        assert "value=None" in log_capture.text

    def test_error_failed_basic(self, logger, log_capture):
        """Should log error with exception details"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.error_failed("operation", e)

        assert "❌" in log_capture.text
        assert "operation failed" in log_capture.text
        assert "Test error" in log_capture.text
        assert "ValueError" in log_capture.text
        assert "Traceback" in log_capture.text

    def test_error_failed_with_context(self, logger, log_capture):
        """Should log error with context"""
        try:
            raise RuntimeError("Something went wrong")
        except RuntimeError as e:
            logger.error_failed("analysis", e, response_id=789)

        assert "❌" in log_capture.text
        assert "analysis failed" in log_capture.text
        assert "response_id=789" in log_capture.text
        assert "Something went wrong" in log_capture.text

    def test_debug(self, logger, caplog):
        """Should log debug message"""
        caplog.set_level(logging.DEBUG)
        logger.debug("debug info", item_count=5)

        assert "🔍" in caplog.text
        assert "debug info" in caplog.text
        assert "item_count=5" in caplog.text

    def test_format_context_empty(self, logger):
        """Should handle empty context"""
        result = logger._format_context({})
        assert result == ""

    def test_format_context_single_item(self, logger):
        """Should format single context item"""
        result = logger._format_context({"key": "value"})
        assert result == " (key=value)"

    def test_format_context_multiple_items(self, logger):
        """Should format multiple context items"""
        result = logger._format_context({"id": 123, "type": "photo", "status": "done"})
        assert " (id=123" in result
        assert "type=photo" in result
        assert "status=done" in result

    def test_format_context_special_values(self, logger):
        """Should handle special values in context"""
        result = logger._format_context({
            "none_val": None,
            "bool_val": True,
            "int_val": 42,
            "list_val": [1, 2, 3]
        })
        assert "none_val=None" in result
        assert "bool_val=True" in result
        assert "int_val=42" in result
        assert "list_val=[1, 2, 3]" in result


class TestGetContextLogger:
    """Tests for get_context_logger factory function"""

    def test_returns_context_logger(self):
        """Should return ContextLogger instance"""
        logger = get_context_logger("test")
        assert isinstance(logger, ContextLogger)

    def test_logger_has_correct_name(self):
        """Should create logger with correct name"""
        logger = get_context_logger("my_module")
        assert logger.logger.name == "my_module"

    def test_creates_different_loggers(self):
        """Should create different logger instances for different names"""
        logger1 = get_context_logger("module1")
        logger2 = get_context_logger("module2")

        assert logger1.logger.name == "module1"
        assert logger2.logger.name == "module2"
        assert logger1.logger is not logger2.logger


class TestContextLoggerIntegration:
    """Integration tests for ContextLogger"""

    @pytest.fixture
    def log_capture(self, caplog):
        """Capture log output"""
        caplog.set_level(logging.INFO)
        return caplog

    def test_typical_operation_lifecycle(self, log_capture):
        """Should handle typical operation start-complete lifecycle"""
        logger = get_context_logger("integration_test")

        logger.info_start("data processing", batch_id=1)
        logger.info_status("processing records", count=100)
        logger.info_complete("data processing", records_processed=100)

        assert "🔄 Starting data processing" in log_capture.text
        assert "📋 processing records" in log_capture.text
        assert "✅ Completed data processing" in log_capture.text

    def test_error_handling_scenario(self, log_capture):
        """Should handle error scenarios properly"""
        logger = get_context_logger("error_test")

        logger.info_start("risky operation", attempt=1)

        try:
            raise ConnectionError("Database connection failed")
        except ConnectionError as e:
            logger.error_failed("risky operation", e, attempt=1)

        assert "🔄 Starting risky operation" in log_capture.text
        assert "❌ risky operation failed" in log_capture.text
        assert "Database connection failed" in log_capture.text
        assert "ConnectionError" in log_capture.text

    def test_multiple_operations_with_context(self, log_capture):
        """Should handle multiple operations with different contexts"""
        logger = get_context_logger("multi_op_test")

        # Operation 1
        logger.info_start("operation1", user_id=1)
        logger.info_complete("operation1", status="success")

        # Operation 2
        logger.info_start("operation2", user_id=2)
        logger.warning("unusual behavior detected", user_id=2)
        logger.info_complete("operation2", status="warning")

        log_text = log_capture.text

        assert "user_id=1" in log_text
        assert "user_id=2" in log_text
        assert "⚠️" in log_text

    def test_real_world_media_analysis_flow(self, log_capture):
        """Should simulate real media analysis flow"""
        logger = get_context_logger("media_analysis")

        response_id = 123
        media_type = "photo"

        logger.info_start("media analysis", response_id=response_id, media_type=media_type)
        logger.info_status("analyzing photo", response_id=response_id)
        logger.debug("photo description", length=150, preview="Test description...")
        logger.info_status("generating reporting labels")
        logger.info_status("labels generated", count=5)
        logger.info_complete("media analysis", response_id=response_id, result_id=456)

        log_text = log_capture.text

        assert "🔄 Starting media analysis" in log_text
        assert "response_id=123" in log_text
        assert "media_type=photo" in log_text
        assert "✅ Completed media analysis" in log_text
        assert "result_id=456" in log_text
