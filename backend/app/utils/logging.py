"""Centralized logging utilities with context and emoji support"""
import logging
import traceback
from typing import Any, Dict, Optional


class ContextLogger:
    """Logger with context and emoji support for consistent logging patterns"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info_start(self, operation: str, **context):
        """Log the start of an operation with context"""
        context_str = self._format_context(context)
        self.logger.info(f"🔄 Starting {operation}{context_str}")

    def info_complete(self, operation: str, **result):
        """Log successful completion of an operation"""
        result_str = self._format_context(result)
        self.logger.info(f"✅ Completed {operation}{result_str}")

    def info_status(self, message: str, **context):
        """Log general info status"""
        context_str = self._format_context(context)
        self.logger.info(f"📋 {message}{context_str}")

    def warning(self, message: str, **context):
        """Log warning with context"""
        context_str = self._format_context(context)
        self.logger.warning(f"⚠️  {message}{context_str}")

    def error_failed(self, operation: str, error: Exception, **context):
        """Log operation failure with full error details"""
        context_str = self._format_context(context)
        self.logger.error(f"❌ {operation} failed{context_str}: {str(error)}")
        self.logger.error(f"❌ Error type: {type(error).__name__}")
        self.logger.error(f"❌ Traceback: {traceback.format_exc()}")

    def debug(self, message: str, **context):
        """Log debug message with context"""
        context_str = self._format_context(context)
        self.logger.debug(f"🔍 {message}{context_str}")

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as readable string"""
        if not context:
            return ""

        items = [f"{k}={v}" for k, v in context.items()]
        return f" ({', '.join(items)})"


def get_context_logger(name: str) -> ContextLogger:
    """Factory function to get a context logger instance"""
    return ContextLogger(name)
