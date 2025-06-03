# CrewAI Examples

This directory contains practical examples demonstrating various CrewAI features and integrations.

## Output Management System Example

### Overview

The `output_management_example.py` demonstrates the comprehensive output management system for CrewAI workflows. This example shows how to:

- Process raw agent outputs into structured formats
- Validate outputs against quality standards and schemas
- Format outputs for different consumption needs
- Aggregate results with analytics and insights
- Generate comprehensive reports

### Running the Example

```bash
# From the project root directory
cd examples
python output_management_example.py
```

### What the Example Does

1. **Simulates Agent Outputs**: Creates realistic outputs from different types of agents (Research, SEO, Content)

2. **Processes Raw Outputs**: Converts unstructured agent outputs into standardized `StructuredOutput` objects with metadata

3. **Validates Quality**: Checks outputs against built-in and custom validation rules

4. **Formats for Multiple Uses**: Converts outputs to JSON, HTML, Markdown, and other formats

5. **Aggregates Results**: Combines outputs with analytics, insights, and quality rankings

6. **Generates Reports**: Creates comprehensive workflow reports in multiple formats

### Generated Output Files

After running the example, you'll find:

- `workflow_report.md` - Comprehensive Markdown report
- `sample_outputs/` - Directory with individual agent outputs in multiple formats
- `sample_outputs/complete_workflow_report.html` - Complete HTML report
- `sample_outputs/workflow_analytics.json` - Workflow analytics data

### Example Output Structure

```
sample_outputs/
├── agent_1_research_specialist.json
├── agent_1_research_specialist.html
├── agent_2_seo_specialist.json
├── agent_2_seo_specialist.html
├── agent_3_content_writer.json
├── agent_3_content_writer.html
├── complete_workflow_report.html
└── workflow_analytics.json
```

### Key Features Demonstrated

1. **Structured Data Models**
   - Consistent output representation
   - Rich metadata tracking
   - Content organization and tagging

2. **Comprehensive Validation**
   - Built-in quality rules
   - Custom business rules
   - Schema validation

3. **Flexible Formatting**
   - Multiple export formats
   - Template-based customization
   - Batch processing capabilities

4. **Advanced Analytics**
   - Workflow performance metrics
   - Agent comparison and ranking
   - Quality insights and recommendations

5. **Result Aggregation**
   - Multiple consolidation strategies
   - Cross-agent analytics
   - Workflow-level insights

### Integration Examples

The example shows how to integrate the output management system with:

- Raw agent outputs of different types
- Validation schemas for different domains
- Custom formatting requirements
- Analytics and reporting needs

### Prerequisites

- Python 3.8+
- Required dependencies (see main requirements.txt)
- CrewAI framework

### Customization

You can customize the example by:

1. **Modifying Agent Outputs**: Edit the `simulate_agent_outputs()` function
2. **Adding Validation Rules**: Create custom rules in the validation section
3. **Changing Output Formats**: Modify the formatting options
4. **Adjusting Analytics**: Customize the aggregation and reporting logic

### Learn More

For detailed documentation on the output management system, see:
- `docs/output_management_guide.md` - Comprehensive guide
- `src/core/output_management/` - Source code with inline documentation

### Troubleshooting

If you encounter issues:

1. **Import Errors**: Ensure you're running from the examples directory
2. **Missing Dependencies**: Install required packages from requirements.txt
3. **Permission Errors**: Ensure write permissions for output directories

For more help, check the troubleshooting section in the main documentation. 