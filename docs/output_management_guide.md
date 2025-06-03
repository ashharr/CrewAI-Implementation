# CrewAI Output Management System

The CrewAI Output Management System provides a comprehensive solution for structuring, validating, formatting, and aggregating agent outputs. This system ensures consistency, quality, and usability of results from multi-agent workflows.

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Quick Start](#quick-start)
4. [Structured Outputs](#structured-outputs)
5. [Output Processing](#output-processing)
6. [Validation System](#validation-system)
7. [Formatting & Export](#formatting--export)
8. [Result Aggregation](#result-aggregation)
9. [Integration Guide](#integration-guide)
10. [Best Practices](#best-practices)
11. [Advanced Usage](#advanced-usage)

## Overview

The Output Management System addresses common challenges in multi-agent workflows:

- **Inconsistent Output Formats**: Agents produce outputs in different formats and structures
- **Quality Assurance**: No standardized validation of output quality
- **Data Processing**: Difficulty in aggregating and analyzing results from multiple agents
- **Format Conversion**: Need to convert outputs for different consumption needs
- **Workflow Analytics**: Lack of insights into workflow performance and quality

### Key Benefits

- ✅ **Standardized Structure**: Consistent data models for all agent outputs
- ✅ **Quality Validation**: Comprehensive validation with custom rules
- ✅ **Multiple Formats**: Export to JSON, HTML, Markdown, CSV, XML
- ✅ **Analytics & Insights**: Workflow performance analysis
- ✅ **Result Aggregation**: Combine outputs with multiple strategies
- ✅ **Extensible**: Easy to add custom validation rules and formats

## Core Components

### 1. StructuredOutput
The core data model that represents a standardized agent output with metadata, validation, and organization.

### 2. OutputProcessor
Processes raw agent outputs into structured formats, extracting metadata and organizing content.

### 3. OutputValidator
Validates outputs against schemas, quality standards, and business rules.

### 4. OutputFormatter
Converts structured outputs to various formats (JSON, HTML, Markdown, etc.).

### 5. ResultAggregator
Aggregates multiple outputs, generates analytics, and creates consolidated results.

## Quick Start

### Basic Usage

```python
from src.core.output_management import (
    OutputProcessor,
    OutputFormatter,
    OutputValidator,
    ResultAggregator,
    RESEARCH_OUTPUT_SCHEMA
)

# Initialize components
processor = OutputProcessor()
validator = OutputValidator()
formatter = OutputFormatter()
aggregator = ResultAggregator()

# Process raw agent output
structured_output = processor.process_agent_output(
    raw_output="Your agent's raw output here...",
    agent_id="agent_1",
    agent_role="Research Specialist",
    task_id="research_task_1",
    workflow_id="workflow_001"
)

# Validate the output
validation = validator.validate_output(
    structured_output, 
    schema=RESEARCH_OUTPUT_SCHEMA
)

# Format for different needs
json_result = formatter.format_output(structured_output, "json")
html_result = formatter.format_output(structured_output, "html")
markdown_result = formatter.format_output(structured_output, "markdown")

print(f"Validation Score: {validation.validation_score:.1%}")
print(f"Valid: {validation.is_valid}")
```

### Integration with CrewAI

```python
from crewai import Crew
from src.core.output_management import OutputProcessor

def enhanced_crew_execution(crew, inputs):
    """Execute crew with output management."""
    processor = OutputProcessor()
    
    # Execute the crew
    result = crew.kickoff(inputs=inputs)
    
    # Process the outputs
    structured_outputs = processor.process_crew_output(
        crew_result=result,
        workflow_id="my_workflow"
    )
    
    return structured_outputs
```

## Structured Outputs

### StructuredOutput Model

```python
class StructuredOutput(BaseModel):
    # Core output data
    id: str                           # Unique identifier
    content: Union[str, Dict, List]   # The actual output content
    output_type: OutputType           # TEXT, JSON, MARKDOWN, HTML, etc.
    status: OutputStatus              # SUCCESS, PARTIAL, FAILED, PENDING
    
    # Metadata and context
    metadata: OutputMetadata          # Agent info, timing, quality metrics
    validation: Optional[OutputValidation]  # Validation results
    
    # Content organization
    sections: Optional[Dict[str, Any]]  # Organized content sections
    tags: List[str]                     # Content tags
    keywords: List[str]                 # Extracted keywords
    
    # Processing information
    processing_notes: List[str]         # Processing observations
    error_details: Optional[str]        # Error information if failed
    
    # File management
    output_file: Optional[str]          # Path to saved file
    backup_files: List[str]             # Backup file paths
```

### OutputMetadata

```python
class OutputMetadata(BaseModel):
    agent_id: str                    # Agent identifier
    agent_role: str                  # Agent role/type
    task_id: Optional[str]           # Task identifier
    task_name: Optional[str]         # Task name
    workflow_id: Optional[str]       # Workflow identifier
    timestamp: datetime              # Generation timestamp
    execution_time: Optional[float]  # Processing time in seconds
    tokens_used: Optional[int]       # AI tokens consumed
    model_used: Optional[str]        # AI model used
    confidence_score: Optional[float] # Confidence in output quality
    source_count: Optional[int]      # Number of sources used
    word_count: Optional[int]        # Word count of content
```

### Creating Structured Outputs

```python
from src.core.output_management import StructuredOutput, OutputMetadata, OutputType

# Manual creation
structured_output = StructuredOutput(
    content="Your content here",
    output_type=OutputType.MARKDOWN,
    metadata=OutputMetadata(
        agent_id="research_agent",
        agent_role="Research Specialist",
        workflow_id="demo_workflow"
    ),
    tags=["research", "AI", "technology"],
    keywords=["artificial intelligence", "machine learning"]
)

# Using OutputProcessor (recommended)
processor = OutputProcessor()
structured_output = processor.process_agent_output(
    raw_output=raw_content,
    agent_id="research_agent",
    agent_role="Research Specialist"
)
```

## Output Processing

### Automatic Content Analysis

The OutputProcessor automatically:

- **Detects Content Type**: JSON, Markdown, HTML, CSV, or plain text
- **Extracts Metadata**: Word count, source count, confidence scores
- **Organizes Sections**: Parses content into logical sections
- **Identifies Tags/Keywords**: Extracts relevant tags and keywords
- **Handles Errors**: Gracefully handles processing errors

### Processing Different Content Types

```python
processor = OutputProcessor()

# Markdown content
markdown_output = processor.process_agent_output(
    raw_output="# Research Report\n\n## Findings\n...",
    agent_id="research_agent",
    agent_role="Research Specialist"
)

# JSON content
json_output = processor.process_agent_output(
    raw_output={"results": ["item1", "item2"], "confidence": 0.95},
    agent_id="data_agent",
    agent_role="Data Analyst"
)

# Plain text content
text_output = processor.process_agent_output(
    raw_output="Simple text output from agent",
    agent_id="simple_agent",
    agent_role="Content Generator"
)
```

### Processing Crew Results

```python
# Process complete crew execution results
structured_outputs = processor.process_crew_output(
    crew_result=crew.kickoff(inputs),
    workflow_id="my_workflow"
)

for output in structured_outputs:
    print(f"Agent: {output.metadata.agent_role}")
    print(f"Status: {output.status}")
    print(f"Word Count: {output.metadata.word_count}")
```

## Validation System

### Built-in Validation Rules

The system includes 10 built-in validation rules:

1. **Content Exists**: Output must have non-empty content
2. **Minimum Length**: Content meets minimum length requirements
3. **Status Consistency**: Status matches actual output state
4. **Metadata Completeness**: Essential metadata fields present
5. **Content Type Consistency**: Content matches declared type
6. **Word Count Accuracy**: Metadata word count is accurate
7. **No Suspicious Content**: Content doesn't contain suspicious patterns
8. **Proper Encoding**: Content is properly encoded
9. **JSON Validity**: JSON outputs are valid JSON
10. **Markdown Structure**: Markdown has proper structure

### Schema Validation

```python
from src.core.output_management import (
    OutputValidator,
    RESEARCH_OUTPUT_SCHEMA,
    CONTENT_OUTPUT_SCHEMA,
    ANALYSIS_OUTPUT_SCHEMA
)

validator = OutputValidator()

# Validate against predefined schema
validation = validator.validate_output(
    output=structured_output,
    schema=RESEARCH_OUTPUT_SCHEMA
)

print(f"Valid: {validation.is_valid}")
print(f"Score: {validation.validation_score:.1%}")
print(f"Errors: {validation.errors}")
print(f"Warnings: {validation.warnings}")
```

### Custom Validation Rules

```python
# Content quality rule
quality_rule = validator.create_content_quality_rule(
    min_word_count=500,
    max_word_count=5000,
    required_keywords=["AI", "machine learning"],
    forbidden_words=["spam", "fake"]
)
validator.add_custom_rule(quality_rule)

# Business logic rule
business_rule = validator.create_business_rule(
    name="company_branding",
    description="Content must mention company name",
    validator_func=lambda output: "MyCompany" in str(output.content),
    error_message="Content missing company branding"
)
validator.add_custom_rule(business_rule)

# Custom ValidationRule
from src.core.output_management import ValidationRule

custom_rule = ValidationRule(
    name="technical_depth",
    description="Technical content should include code examples",
    validator_func=lambda output: "```" in str(output.content) if "technical" in output.tags else True,
    error_message="Technical content missing code examples",
    warning_only=True,
    weight=1.5
)
validator.add_custom_rule(custom_rule)
```

### Validation Summary

```python
# Validate multiple outputs
validations = validator.validate_multiple_outputs(
    outputs=structured_outputs,
    schema=RESEARCH_OUTPUT_SCHEMA,
    strict_mode=False
)

# Get summary statistics
summary = validator.get_validation_summary(validations)
print(f"Success Rate: {summary['success_rate']:.1%}")
print(f"Average Score: {summary['avg_validation_score']:.1%}")
print(f"Total Errors: {summary['total_errors']}")
```

## Formatting & Export

### Supported Formats

- **JSON**: Structured data with full metadata
- **HTML**: Web-ready format with styling
- **Markdown**: Documentation-friendly format
- **CSV**: Tabular data for analysis
- **XML**: Structured markup format
- **Summary**: Concise overview format
- **Template**: Custom Jinja2 templates

### Basic Formatting

```python
formatter = OutputFormatter()

# Format single output
json_result = formatter.format_output(structured_output, "json")
html_result = formatter.format_output(structured_output, "html")
markdown_result = formatter.format_output(structured_output, "markdown")

# Format with options
formatted = formatter.format_output(
    structured_output,
    "html",
    custom_options={
        "include_css": True,
        "include_metadata": True
    }
)
```

### Multiple Output Formatting

```python
# Aggregate multiple outputs
aggregated_report = formatter.format_multiple_outputs(
    outputs=structured_outputs,
    target_format="html",
    aggregate=True,
    custom_options={"title": "Workflow Results Report"}
)

# Individual formatting
individual_reports = formatter.format_multiple_outputs(
    outputs=structured_outputs,
    target_format="markdown",
    aggregate=False
)
```

### Custom Templates

```python
# Using Jinja2 templates
formatter = OutputFormatter(template_dir="./templates")

template_result = formatter.format_output(
    structured_output,
    "template",
    template_name="custom_report.html",
    custom_options={"company_name": "MyCompany"}
)
```

### Saving Formatted Outputs

```python
from pathlib import Path

# Save individual outputs
output_dir = Path("exports")
output_dir.mkdir(exist_ok=True)

for i, output in enumerate(structured_outputs):
    # HTML format
    html_content = formatter.format_output(output, "html")
    html_file = output_dir / f"output_{i+1}.html"
    html_file.write_text(html_content, encoding="utf-8")
    
    # JSON format
    json_content = formatter.format_output(output, "json")
    json_file = output_dir / f"output_{i+1}.json"
    json_file.write_text(json_content, encoding="utf-8")
```

## Result Aggregation

### Workflow Analytics

```python
aggregator = ResultAggregator()

# Create workflow result with analytics
workflow_result = aggregator.aggregate_workflow_results(
    outputs=structured_outputs,
    workflow_id="research_workflow_001",
    workflow_name="AI Research Analysis",
    execution_start=start_time,
    execution_end=end_time
)

# Access analytics
analytics = workflow_result.analytics
print(f"Success Rate: {analytics['success_rate']:.1%}")
print(f"Total Words: {analytics['content_metrics']['total_words']:,}")
print(f"Agent Performance: {analytics['agent_performance']}")

# Get insights
insights = workflow_result.insights
for insight in insights:
    print(f"💡 {insight}")
```

### Output Consolidation

```python
# Merge strategy - combines all outputs
merged_output = aggregator.create_consolidated_output(
    outputs=structured_outputs,
    consolidation_strategy="merge",
    target_agent_role="Consolidated Research Team"
)

# Summary strategy - creates executive summary
summary_output = aggregator.create_consolidated_output(
    outputs=structured_outputs,
    consolidation_strategy="summary",
    target_agent_role="Executive Summary Agent"
)

# Best strategy - selects highest quality output
best_output = aggregator.create_consolidated_output(
    outputs=structured_outputs,
    consolidation_strategy="best",
    target_agent_role="Best Output Selector"
)
```

### Performance Comparison

```python
# Generate detailed comparison
comparison = aggregator.generate_comparison_report(
    outputs=structured_outputs,
    comparison_criteria=["word_count", "execution_time", "validation_score"]
)

# View rankings
for rank_info in comparison["ranking"]:
    print(f"{rank_info['rank']}. {rank_info['agent']}")
    print(f"   Score: {rank_info['score']:.1f}")
    print(f"   Status: {rank_info['status']}")
```

## Integration Guide

### CrewAI Integration

```python
from crewai import Crew, Agent, Task
from src.core.output_management import OutputProcessor, OutputValidator

class EnhancedCrew:
    def __init__(self):
        self.processor = OutputProcessor()
        self.validator = OutputValidator()
        
    def execute_with_output_management(self, crew, inputs):
        """Execute crew with enhanced output management."""
        
        # Execute crew
        start_time = datetime.now()
        result = crew.kickoff(inputs=inputs)
        end_time = datetime.now()
        
        # Process outputs
        structured_outputs = self.processor.process_crew_output(
            crew_result=result,
            workflow_id=inputs.get('workflow_id', 'default')
        )
        
        # Validate outputs
        for output in structured_outputs:
            validation = self.validator.validate_output(output)
            output.validation = validation
        
        return structured_outputs
```

### Task-Level Integration

```python
# Add output processing to task completion
@task
def enhanced_research_task(self) -> Task:
    def task_callback(task_output):
        """Process task output when completed."""
        processor = OutputProcessor()
        structured = processor.process_agent_output(
            raw_output=task_output.raw,
            agent_id=task_output.agent.id if hasattr(task_output.agent, 'id') else 'unknown',
            agent_role=task_output.agent.role,
            task_id=self.tasks_config['research_task'].get('id', 'research'),
            workflow_id=self.workflow_id
        )
        
        # Store structured output for later use
        self.structured_outputs.append(structured)
    
    return Task(
        config=self.tasks_config['research_task'],
        callback=task_callback
    )
```

### Workflow Manager Integration

```python
from src.core.orchestrator import CrewManager
from src.core.output_management import OutputProcessor, ResultAggregator

class EnhancedCrewManager(CrewManager):
    def __init__(self):
        super().__init__()
        self.output_processor = OutputProcessor()
        self.aggregator = ResultAggregator()
        
    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None):
        """Enhanced workflow execution with output management."""
        
        # Execute base workflow
        base_result = super().execute_workflow(workflow_id, inputs)
        
        # Process outputs
        structured_outputs = self.output_processor.process_crew_output(
            crew_result=base_result['result'],
            workflow_id=workflow_id
        )
        
        # Generate analytics
        workflow_result = self.aggregator.aggregate_workflow_results(
            outputs=structured_outputs,
            workflow_id=workflow_id,
            workflow_name=f"Workflow {workflow_id}"
        )
        
        # Enhanced result
        return {
            **base_result,
            'structured_outputs': structured_outputs,
            'workflow_analytics': workflow_result.analytics,
            'workflow_insights': workflow_result.insights
        }
```

## Best Practices

### 1. Output Structure Design

```python
# ✅ Good: Use appropriate output types
processor.process_agent_output(
    raw_output=markdown_content,
    agent_id="research_agent",
    agent_role="Research Specialist",
    task_name="Market Research Analysis"
)

# ❌ Avoid: Generic task naming
processor.process_agent_output(
    raw_output=content,
    agent_id="agent1",
    agent_role="Agent",
    task_name="Task"
)
```

### 2. Validation Strategy

```python
# ✅ Good: Use appropriate schemas
if agent_role == "Research Specialist":
    schema = RESEARCH_OUTPUT_SCHEMA
elif agent_role == "Content Writer":
    schema = CONTENT_OUTPUT_SCHEMA
else:
    schema = None

validation = validator.validate_output(output, schema=schema)

# ✅ Good: Handle validation results
if not validation.is_valid:
    logger.warning(f"Output validation failed: {validation.errors}")
    # Handle failed validation appropriately
```

### 3. Error Handling

```python
# ✅ Good: Graceful error handling
try:
    structured_output = processor.process_agent_output(
        raw_output=raw_output,
        agent_id=agent_id,
        agent_role=agent_role
    )
except Exception as e:
    logger.error(f"Output processing failed: {e}")
    # Create fallback structured output
    structured_output = StructuredOutput(
        content=str(raw_output),
        output_type=OutputType.TEXT,
        status=OutputStatus.FAILED,
        metadata=OutputMetadata(
            agent_id=agent_id,
            agent_role=agent_role
        ),
        error_details=str(e)
    )
```

### 4. Performance Optimization

```python
# ✅ Good: Batch processing
structured_outputs = []
for raw_output, metadata in raw_outputs_batch:
    structured = processor.process_agent_output(
        raw_output=raw_output,
        **metadata
    )
    structured_outputs.append(structured)

# Batch validate
validations = validator.validate_multiple_outputs(structured_outputs)
```

### 5. Memory Management

```python
# ✅ Good: Clear large outputs when done
def process_large_workflow(outputs):
    structured_outputs = []
    
    for output in outputs:
        structured = processor.process_agent_output(output)
        structured_outputs.append(structured)
        
        # Clear raw output to save memory
        del output
    
    return structured_outputs
```

## Advanced Usage

### Custom Output Types

```python
from src.core.output_management import OutputType
from enum import Enum

class CustomOutputType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    BINARY = "binary"

# Extend processor for custom types
class CustomOutputProcessor(OutputProcessor):
    def _determine_output_type(self, raw_output):
        if isinstance(raw_output, bytes):
            return CustomOutputType.BINARY, raw_output
        return super()._determine_output_type(raw_output)
```

### Custom Validation Logic

```python
class DomainSpecificValidator(OutputValidator):
    def __init__(self, domain_rules):
        super().__init__()
        self.domain_rules = domain_rules
        
    def validate_domain_output(self, output, domain):
        """Validate output against domain-specific rules."""
        if domain in self.domain_rules:
            rules = self.domain_rules[domain]
            return self.validate_output(output, custom_rules=rules)
        return super().validate_output(output)
```

### Custom Formatters

```python
class PDFFormatter(OutputFormatter):
    def format_as_pdf(self, output, options=None):
        """Convert output to PDF format."""
        # Implementation for PDF generation
        html_content = self._format_as_html(output, options or {})
        # Convert HTML to PDF using library like weasyprint
        return self._html_to_pdf(html_content)
```

### Workflow Templates

```python
# Create reusable workflow templates
RESEARCH_WORKFLOW_TEMPLATE = {
    "validation_rules": [
        "content_quality",
        "source_validation",
        "fact_checking"
    ],
    "output_formats": ["html", "markdown", "json"],
    "consolidation_strategy": "merge",
    "quality_threshold": 0.8
}

def execute_template_workflow(crew, inputs, template):
    """Execute workflow using template configuration."""
    # Apply template settings
    validator = OutputValidator()
    for rule_name in template["validation_rules"]:
        # Add rules based on template
        pass
    
    # Execute with template settings
    return enhanced_execution(crew, inputs, validator, template)
```

## Troubleshooting

### Common Issues

1. **Validation Failures**
   ```python
   # Check validation details
   if not validation.is_valid:
       print("Validation Errors:")
       for error in validation.errors:
           print(f"  - {error}")
   ```

2. **Memory Issues with Large Outputs**
   ```python
   # Process in smaller batches
   batch_size = 10
   for i in range(0, len(outputs), batch_size):
       batch = outputs[i:i+batch_size]
       process_batch(batch)
   ```

3. **Format Conversion Errors**
   ```python
   # Handle format conversion gracefully
   try:
       formatted = formatter.format_output(output, "html")
   except Exception as e:
       logger.warning(f"HTML formatting failed: {e}")
       formatted = formatter.format_output(output, "markdown")
   ```

## Performance Tips

1. **Use Appropriate Batch Sizes**: Process outputs in batches of 10-50 items
2. **Cache Validation Results**: Cache validation results for identical outputs
3. **Lazy Loading**: Only process outputs when needed
4. **Memory Cleanup**: Clear large outputs after processing
5. **Parallel Processing**: Use multiprocessing for large workloads

## Conclusion

The CrewAI Output Management System provides a comprehensive solution for handling agent outputs in multi-agent workflows. By using structured data models, comprehensive validation, flexible formatting, and powerful aggregation capabilities, you can ensure your CrewAI workflows produce consistent, high-quality, and actionable results.

For more examples and detailed API documentation, see the `examples/` directory and run the demonstration script:

```bash
python examples/output_management_example.py
``` 