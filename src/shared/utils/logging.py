"""
Structured logging configuration for the AI Agent Platform.
"""

import logging
import sys
from typing import Any, Dict

import structlog

from src.shared.config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.logging.format == "json"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.logging.level.upper()),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def add_correlation_id(correlation_id: str) -> Dict[str, Any]:
    """Add correlation ID to log context."""
    return {"correlation_id": correlation_id}


def add_user_context(user_id: str, username: str = None) -> Dict[str, Any]:
    """Add user context to log context."""
    context = {"user_id": user_id}
    if username:
        context["username"] = username
    return context


def add_service_context(service_name: str) -> Dict[str, Any]:
    """Add service context to log context."""
    return {"service": service_name} 