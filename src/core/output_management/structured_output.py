"""
Structured Output Management for CrewAI Agents

Provides standardized data structures and schemas for agent outputs
to ensure consistency and easy processing across workflows.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Type
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict
import json
import uuid


class OutputType(str, Enum):
    """Enumeration of supported output types."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"
    XML = "xml"
    YAML = "yaml"
    

class OutputStatus(str, Enum):
    """Enumeration of output processing statuses."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"


class OutputMetadata(BaseModel):
    """Metadata associated with agent outputs."""
    
    model_config = ConfigDict(protected_namespaces=())
    
    agent_id: str = Field(..., description="ID of the agent that produced the output")
    agent_role: str = Field(..., description="Role of the agent")
    task_id: Optional[str] = Field(None, description="ID of the task that generated the output")
    task_name: Optional[str] = Field(None, description="Name of the task")
    workflow_id: Optional[str] = Field(None, description="ID of the parent workflow")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the output was generated")
    execution_time: Optional[float] = Field(None, description="Time taken to generate output in seconds")
    tokens_used: Optional[int] = Field(None, description="Number of tokens consumed")
    model_used: Optional[str] = Field(None, description="AI model used for generation")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in the output quality")
    source_count: Optional[int] = Field(None, description="Number of sources used")
    word_count: Optional[int] = Field(None, description="Word count of the output")
    

class OutputValidation(BaseModel):
    """Validation results for agent outputs."""
    
    is_valid: bool = Field(..., description="Whether the output passes validation")
    validation_score: float = Field(..., ge=0.0, le=1.0, description="Validation score")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    requirements_met: Dict[str, bool] = Field(default_factory=dict, description="Requirements satisfaction mapping")
    

class StructuredOutput(BaseModel):
    """
    Standardized structure for agent outputs with metadata and validation.
    """
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    # Core output data
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique output identifier")
    content: Union[str, Dict[str, Any], List[Any]] = Field(..., description="The actual output content")
    output_type: OutputType = Field(default=OutputType.TEXT, description="Type of output content")
    status: OutputStatus = Field(default=OutputStatus.SUCCESS, description="Processing status")
    
    # Metadata and context
    metadata: OutputMetadata = Field(..., description="Output metadata")
    validation: Optional[OutputValidation] = Field(None, description="Validation results")
    
    # Content organization
    sections: Optional[Dict[str, Any]] = Field(None, description="Organized content sections")
    tags: List[str] = Field(default_factory=list, description="Content tags for categorization")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    
    # Processing information
    processing_notes: List[str] = Field(default_factory=list, description="Processing notes and observations")
    error_details: Optional[str] = Field(None, description="Detailed error information if status is FAILED")
    
    # File management
    output_file: Optional[str] = Field(None, description="Path to output file if saved")
    backup_files: List[str] = Field(default_factory=list, description="Backup file paths")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper JSON serialization."""
        return json.loads(self.model_dump_json())
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to formatted JSON string."""
        return self.model_dump_json(indent=indent)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the output for quick overview."""
        return {
            "id": self.id,
            "agent_role": self.metadata.agent_role,
            "status": self.status,
            "output_type": self.output_type,
            "timestamp": self.metadata.timestamp,
            "word_count": self.metadata.word_count,
            "validation_score": self.validation.validation_score if self.validation else None,
            "tags": self.tags[:5],  # First 5 tags
            "has_errors": bool(self.validation and self.validation.errors) if self.validation else False
        }
    
    def get_content_preview(self, max_length: int = 200) -> str:
        """Get a preview of the content."""
        if isinstance(self.content, str):
            return self.content[:max_length] + ("..." if len(self.content) > max_length else "")
        elif isinstance(self.content, dict):
            return str(self.content)[:max_length] + ("..." if len(str(self.content)) > max_length else "")
        else:
            return str(self.content)[:max_length] + ("..." if len(str(self.content)) > max_length else "")


class OutputSchema(BaseModel):
    """
    Schema definition for expected agent outputs.
    Used to validate and structure agent responses.
    """
    
    name: str = Field(..., description="Schema name")
    description: str = Field(..., description="Schema description")
    version: str = Field(default="1.0", description="Schema version")
    
    # Content requirements
    required_fields: List[str] = Field(default_factory=list, description="Required content fields")
    optional_fields: List[str] = Field(default_factory=list, description="Optional content fields")
    field_types: Dict[str, str] = Field(default_factory=dict, description="Expected field types")
    
    # Validation rules
    min_word_count: Optional[int] = Field(None, description="Minimum word count")
    max_word_count: Optional[int] = Field(None, description="Maximum word count")
    required_sections: List[str] = Field(default_factory=list, description="Required content sections")
    format_requirements: Dict[str, Any] = Field(default_factory=dict, description="Format-specific requirements")
    
    # Quality requirements
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence score")
    required_sources: Optional[int] = Field(None, description="Minimum number of sources required")
    
    def validate_output(self, output: StructuredOutput) -> OutputValidation:
        """Validate an output against this schema."""
        errors = []
        warnings = []
        requirements_met = {}
        
        # Check word count
        if self.min_word_count and output.metadata.word_count:
            if output.metadata.word_count < self.min_word_count:
                errors.append(f"Word count {output.metadata.word_count} below minimum {self.min_word_count}")
                requirements_met["min_word_count"] = False
            else:
                requirements_met["min_word_count"] = True
        
        if self.max_word_count and output.metadata.word_count:
            if output.metadata.word_count > self.max_word_count:
                warnings.append(f"Word count {output.metadata.word_count} exceeds maximum {self.max_word_count}")
                requirements_met["max_word_count"] = False
            else:
                requirements_met["max_word_count"] = True
        
        # Check confidence score
        if output.metadata.confidence_score:
            if output.metadata.confidence_score < self.min_confidence:
                warnings.append(f"Confidence score {output.metadata.confidence_score} below minimum {self.min_confidence}")
                requirements_met["min_confidence"] = False
            else:
                requirements_met["min_confidence"] = True
        
        # Check required sources
        if self.required_sources and output.metadata.source_count:
            if output.metadata.source_count < self.required_sources:
                errors.append(f"Source count {output.metadata.source_count} below required {self.required_sources}")
                requirements_met["required_sources"] = False
            else:
                requirements_met["required_sources"] = True
        
        # Check required sections
        if self.required_sections and output.sections:
            for section in self.required_sections:
                if section not in output.sections:
                    errors.append(f"Required section '{section}' missing")
                    requirements_met[f"section_{section}"] = False
                else:
                    requirements_met[f"section_{section}"] = True
        
        # Calculate validation score
        total_requirements = len(requirements_met)
        met_requirements = sum(1 for met in requirements_met.values() if met)
        validation_score = met_requirements / total_requirements if total_requirements > 0 else 1.0
        
        # Determine if valid (no errors)
        is_valid = len(errors) == 0
        
        return OutputValidation(
            is_valid=is_valid,
            validation_score=validation_score,
            errors=errors,
            warnings=warnings,
            requirements_met=requirements_met
        )


# Predefined schemas for common use cases
RESEARCH_OUTPUT_SCHEMA = OutputSchema(
    name="research_output",
    description="Schema for research task outputs",
    required_fields=["findings", "sources", "summary"],
    optional_fields=["statistics", "quotes", "trends"],
    required_sections=["executive_summary", "key_findings", "sources"],
    min_word_count=500,
    max_word_count=5000,
    required_sources=3
)

CONTENT_OUTPUT_SCHEMA = OutputSchema(
    name="content_output", 
    description="Schema for content creation outputs",
    required_fields=["title", "content", "meta_description"],
    optional_fields=["tags", "keywords", "call_to_action"],
    required_sections=["introduction", "body", "conclusion"],
    min_word_count=800,
    max_word_count=3000,
    min_confidence=0.8
)

ANALYSIS_OUTPUT_SCHEMA = OutputSchema(
    name="analysis_output",
    description="Schema for analytical task outputs", 
    required_fields=["analysis", "insights", "recommendations"],
    optional_fields=["data_points", "charts", "metrics"],
    required_sections=["overview", "detailed_analysis", "recommendations"],
    min_word_count=300,
    max_word_count=2000,
    required_sources=2
) 