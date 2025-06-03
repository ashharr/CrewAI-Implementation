"""
Output Management System for CrewAI

Provides structured output handling, formatting, and processing capabilities
for multi-agent workflows to ensure consistent and usable results.
"""

from .output_formatter import OutputFormatter
from .output_validator import OutputValidator, ValidationRule
from .output_processor import OutputProcessor
from .structured_output import (
    StructuredOutput, 
    OutputMetadata, 
    OutputValidation, 
    OutputSchema,
    OutputType,
    OutputStatus,
    RESEARCH_OUTPUT_SCHEMA,
    CONTENT_OUTPUT_SCHEMA,
    ANALYSIS_OUTPUT_SCHEMA
)
from .result_aggregator import ResultAggregator, WorkflowResult

__all__ = [
    "OutputFormatter",
    "OutputValidator",
    "ValidationRule", 
    "OutputProcessor",
    "StructuredOutput",
    "OutputMetadata",
    "OutputValidation",
    "OutputSchema",
    "OutputType",
    "OutputStatus",
    "RESEARCH_OUTPUT_SCHEMA",
    "CONTENT_OUTPUT_SCHEMA", 
    "ANALYSIS_OUTPUT_SCHEMA",
    "ResultAggregator",
    "WorkflowResult"
] 