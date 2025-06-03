#!/usr/bin/env python
"""
CrewAI Output Management System Example

This example demonstrates how to use the new output management system
to properly structure, validate, format, and aggregate agent outputs.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.output_management import (
    StructuredOutput,
    OutputMetadata,
    OutputType,
    OutputStatus,
    OutputProcessor,
    OutputFormatter,
    OutputValidator,
    ValidationRule,
    ResultAggregator,
    RESEARCH_OUTPUT_SCHEMA,
    CONTENT_OUTPUT_SCHEMA
)


def simulate_agent_outputs():
    """Simulate raw outputs from different agents."""
    
    # Research Agent Output (Markdown)
    research_output = """
# AI Development Research Report

## Executive Summary
Artificial Intelligence development in 2024 has seen remarkable advances in several key areas including large language models, computer vision, and autonomous systems.

## Key Findings

### 1. Large Language Models
- **GPT-4 and Beyond**: Continued improvements in reasoning capabilities
- **Multimodal Integration**: Text, image, and audio processing in unified models
- **Efficiency Gains**: Smaller models achieving comparable performance

### 2. Computer Vision
- **Real-time Processing**: New architectures enabling faster inference
- **3D Understanding**: Improved depth estimation and spatial reasoning
- **Medical Applications**: Enhanced diagnostic capabilities

### 3. Autonomous Systems
- **Self-Driving Cars**: Level 4 autonomy in controlled environments
- **Robotics**: Better manipulation and navigation in complex environments
- **Drones**: Enhanced autonomous flight capabilities

## Sources
1. OpenAI Technical Report 2024
2. Google AI Research Publications
3. MIT Technology Review - AI Advances
4. Stanford AI Index Report 2024
5. Nature Machine Intelligence Journal

## Recommendations
- Invest in multimodal AI research
- Focus on efficiency optimization
- Prioritize safety and ethics in autonomous systems

**Confidence Score**: 0.92
**Research Quality**: High
"""

    # SEO Specialist Output (JSON)
    seo_output = {
        "title": "The Future of AI Development: Trends and Innovations in 2024",
        "meta_description": "Discover the latest AI development trends, breakthrough technologies, and future innovations shaping artificial intelligence in 2024.",
        "keywords": ["AI development", "machine learning", "artificial intelligence", "2024 trends", "technology innovation"],
        "content_structure": {
            "h1": "The Future of AI Development: Trends and Innovations in 2024",
            "h2_sections": [
                "Revolutionary Advances in Large Language Models",
                "Computer Vision Breakthroughs",
                "Autonomous Systems Evolution",
                "Future Implications and Opportunities"
            ]
        },
        "seo_recommendations": {
            "word_count_target": "2000-2500",
            "keyword_density": "2-3%",
            "internal_links": 5,
            "external_links": 8,
            "readability_score": "Grade 8-10"
        },
        "performance_metrics": {
            "estimated_traffic": "15,000-25,000 monthly visits",
            "competition_level": "medium",
            "ranking_potential": "high"
        }
    }

    # Content Writer Output (Markdown)
    content_output = """
# The Future of AI Development: Trends and Innovations in 2024

Artificial Intelligence continues to reshape our world at an unprecedented pace. As we navigate through 2024, the landscape of AI development presents exciting opportunities and transformative technologies that promise to revolutionize industries across the globe.

## Revolutionary Advances in Large Language Models

The evolution of large language models has reached new heights this year. **GPT-4 and its successors** have demonstrated remarkable improvements in reasoning capabilities, while **multimodal integration** allows these systems to seamlessly process text, images, and audio within unified frameworks.

Perhaps most importantly, we're witnessing significant **efficiency gains** where smaller models achieve performance levels previously reserved for massive systems. This democratization of AI capabilities opens doors for broader adoption across various sectors.

## Computer Vision Breakthroughs

Computer vision technology has made substantial leaps forward:

- **Real-time Processing**: New neural architectures enable faster inference without compromising accuracy
- **3D Understanding**: Enhanced depth estimation and spatial reasoning capabilities
- **Medical Applications**: AI-powered diagnostic tools showing remarkable precision in detecting diseases

## Autonomous Systems Evolution

The autonomous systems sector continues to mature:

### Self-Driving Vehicles
Level 4 autonomy is now a reality in controlled environments, with major manufacturers rolling out commercial applications in specific geographic areas.

### Robotics Innovation
Modern robots demonstrate improved manipulation skills and navigation capabilities in complex, dynamic environments.

### Drone Technology
Enhanced autonomous flight systems enable sophisticated applications in delivery, surveillance, and emergency response.

## Future Implications and Opportunities

As we look ahead, several key opportunities emerge:

1. **Investment in Multimodal Research**: Organizations should prioritize developing AI systems that can process multiple data types simultaneously
2. **Efficiency Optimization**: Focus on creating more efficient models that deliver high performance with reduced computational requirements
3. **Safety and Ethics**: Establish robust frameworks for responsible AI development, particularly in autonomous systems

## Conclusion

The AI development landscape in 2024 represents a pivotal moment in technological history. With breakthrough advances in language models, computer vision, and autonomous systems, we stand at the threshold of an era where artificial intelligence becomes deeply integrated into every aspect of human life.

Organizations that embrace these trends while maintaining focus on ethical development and practical applications will be best positioned to thrive in this AI-driven future.

---

*Keywords: AI development, machine learning, artificial intelligence, 2024 trends, technology innovation*
*Word Count: 1,847*
*Confidence: 0.89*
"""

    return [
        ("research_agent", "Research Specialist", research_output),
        ("seo_agent", "SEO Specialist", seo_output),
        ("content_agent", "Content Writer", content_output)
    ]


def demonstrate_output_processing():
    """Demonstrate the output processing capabilities."""
    print("🔄 Starting Output Processing Demonstration\n")
    
    # Initialize the processor
    processor = OutputProcessor()
    
    # Get simulated agent outputs
    raw_outputs = simulate_agent_outputs()
    structured_outputs = []
    
    print("📊 Processing Raw Agent Outputs:")
    print("=" * 50)
    
    for i, (agent_id, agent_role, raw_output) in enumerate(raw_outputs):
        print(f"\n{i+1}. Processing {agent_role} output...")
        
        # Process the raw output
        structured = processor.process_agent_output(
            raw_output=raw_output,
            agent_id=agent_id,
            agent_role=agent_role,
            task_id=f"task_{i+1}",
            task_name=f"{agent_role} Task",
            workflow_id="demo_workflow_001",
            execution_time=2.5 + i * 0.8  # Simulate different execution times
        )
        
        structured_outputs.append(structured)
        
        # Print summary
        summary = structured.get_summary()
        print(f"   ✅ Status: {summary['status']}")
        print(f"   📝 Type: {summary['output_type']}")
        print(f"   📊 Words: {summary['word_count']}")
        print(f"   🏷️  Tags: {', '.join(summary['tags'][:3])}")
        print(f"   🔍 Preview: {structured.get_content_preview(80)}")
    
    return structured_outputs


def demonstrate_validation():
    """Demonstrate the validation capabilities."""
    print("\n\n🔍 Starting Validation Demonstration\n")
    
    # Initialize validator
    validator = OutputValidator()
    
    # Add a custom content quality rule
    quality_rule = validator.create_content_quality_rule(
        min_word_count=100,
        max_word_count=10000,
        required_keywords=["AI", "development"],
        forbidden_words=["spam", "fake"]
    )
    validator.add_custom_rule(quality_rule)
    
    # Add a business rule
    business_rule = validator.create_business_rule(
        name="professional_tone",
        description="Content should maintain professional tone",
        validator_func=lambda output: "awesome" not in str(output.content).lower(),
        error_message="Content contains unprofessional language",
        warning_only=True
    )
    validator.add_custom_rule(business_rule)
    
    print("🔍 Validation Rules Applied:")
    print("=" * 50)
    print("✓ Schema validation (Research/Content schemas)")
    print("✓ Built-in quality rules (10 rules)")
    print("✓ Custom content quality rule")
    print("✓ Custom business rule")
    
    # Get structured outputs
    structured_outputs = demonstrate_output_processing()
    
    print(f"\n📋 Validating {len(structured_outputs)} outputs:")
    print("=" * 50)
    
    validations = []
    for i, output in enumerate(structured_outputs):
        # Select appropriate schema
        schema = None
        if "research" in output.metadata.agent_role.lower():
            schema = RESEARCH_OUTPUT_SCHEMA
        elif "content" in output.metadata.agent_role.lower():
            schema = CONTENT_OUTPUT_SCHEMA
        
        # Validate the output
        validation = validator.validate_output(output, schema=schema)
        validations.append(validation)
        
        print(f"\n{i+1}. {output.metadata.agent_role}:")
        print(f"   ✅ Valid: {validation.is_valid}")
        print(f"   📊 Score: {validation.validation_score:.1%}")
        print(f"   ❌ Errors: {len(validation.errors)}")
        print(f"   ⚠️  Warnings: {len(validation.warnings)}")
        
        if validation.errors:
            for error in validation.errors[:2]:  # Show first 2 errors
                print(f"      ❌ {error}")
        
        if validation.warnings:
            for warning in validation.warnings[:2]:  # Show first 2 warnings
                print(f"      ⚠️ {warning}")
    
    # Generate validation summary
    summary = validator.get_validation_summary(validations)
    print(f"\n📈 Validation Summary:")
    print("=" * 30)
    print(f"Total Validations: {summary['total_validations']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print(f"Average Score: {summary['avg_validation_score']:.1%}")
    print(f"Total Errors: {summary['total_errors']}")
    print(f"Total Warnings: {summary['total_warnings']}")
    
    return structured_outputs, validations


def demonstrate_formatting():
    """Demonstrate the formatting capabilities."""
    print("\n\n🎨 Starting Formatting Demonstration\n")
    
    # Get validated outputs
    structured_outputs, validations = demonstrate_validation()
    
    # Initialize formatter
    formatter = OutputFormatter()
    
    print("🎨 Available Formats:")
    print("=" * 30)
    formats = ["json", "html", "markdown", "csv", "xml", "summary"]
    for fmt in formats:
        print(f"✓ {fmt.upper()}")
    
    # Demonstrate individual formatting
    sample_output = structured_outputs[0]  # Use first output as example
    
    print(f"\n📄 Formatting Sample Output ({sample_output.metadata.agent_role}):")
    print("=" * 60)
    
    # JSON Format
    json_result = formatter.format_output(sample_output, "json", custom_options={"indent": 2})
    print(f"\n🔧 JSON Format (first 200 chars):")
    print(json_result[:200] + "...")
    
    # Summary Format
    summary_result = formatter.format_output(sample_output, "summary")
    print(f"\n📋 Summary Format:")
    print(summary_result)
    
    # Demonstrate multiple output formatting
    print(f"\n📊 Formatting Multiple Outputs:")
    print("=" * 40)
    
    # Aggregate as Markdown report
    markdown_report = formatter.format_multiple_outputs(
        structured_outputs,
        "markdown",
        aggregate=True,
        custom_options={"title": "AI Development Research Workflow Results"}
    )
    
    # Save to file for inspection
    output_file = Path("workflow_report.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_report)
    
    print(f"✅ Generated comprehensive Markdown report: {output_file}")
    print(f"📊 Report length: {len(markdown_report):,} characters")
    
    return structured_outputs


def demonstrate_aggregation():
    """Demonstrate the result aggregation capabilities."""
    print("\n\n📈 Starting Aggregation Demonstration\n")
    
    # Get structured outputs
    structured_outputs = demonstrate_formatting()
    
    # Initialize aggregator
    aggregator = ResultAggregator()
    
    print("📈 Aggregation Capabilities:")
    print("=" * 40)
    print("✓ Workflow analytics and insights")
    print("✓ Output consolidation strategies")
    print("✓ Performance comparisons")
    print("✓ Quality rankings")
    
    # Create workflow result
    workflow_result = aggregator.aggregate_workflow_results(
        outputs=structured_outputs,
        workflow_id="demo_workflow_001",
        workflow_name="AI Development Research Workflow",
        execution_start=datetime.now().replace(second=0, microsecond=0),
        execution_end=datetime.now()
    )
    
    print(f"\n📊 Workflow Analytics:")
    print("=" * 30)
    analytics = workflow_result.analytics
    print(f"Total Outputs: {analytics['total_outputs']}")
    print(f"Success Rate: {analytics['success_rate']:.1%}")
    print(f"Total Words: {analytics['content_metrics']['total_words']:,}")
    print(f"Execution Time: {workflow_result.execution_time:.2f}s")
    print(f"Agent Count: {analytics['agent_count']}")
    
    print(f"\n💡 Workflow Insights:")
    print("=" * 25)
    for insight in workflow_result.insights:
        print(f"   {insight}")
    
    # Demonstrate consolidation strategies
    print(f"\n🔄 Testing Consolidation Strategies:")
    print("=" * 45)
    
    strategies = ["merge", "summary", "best"]
    for strategy in strategies:
        consolidated = aggregator.create_consolidated_output(
            structured_outputs,
            consolidation_strategy=strategy,
            target_agent_role=f"Consolidated Agent ({strategy.title()})"
        )
        
        preview = consolidated.get_content_preview(100)
        print(f"\n✓ {strategy.title()} Strategy:")
        print(f"   Words: {consolidated.metadata.word_count:,}")
        print(f"   Preview: {preview}")
    
    # Generate comparison report
    comparison = aggregator.generate_comparison_report(structured_outputs)
    
    print(f"\n🏆 Agent Performance Ranking:")
    print("=" * 35)
    for rank_info in comparison["ranking"]:
        print(f"{rank_info['rank']}. {rank_info['agent']}")
        print(f"   Score: {rank_info['score']:.1f}")
        print(f"   Status: {rank_info['status']}")
        print(f"   Words: {rank_info['word_count'] or 'N/A'}")
    
    return workflow_result


def save_sample_outputs():
    """Save sample outputs in different formats for reference."""
    print("\n\n💾 Saving Sample Outputs\n")
    
    # Get final workflow result
    workflow_result = demonstrate_aggregation()
    
    formatter = OutputFormatter()
    output_dir = Path("sample_outputs")
    output_dir.mkdir(exist_ok=True)
    
    print("💾 Generating Sample Files:")
    print("=" * 30)
    
    # Save individual outputs in different formats
    for i, output in enumerate(workflow_result.outputs):
        base_name = f"agent_{i+1}_{output.metadata.agent_role.lower().replace(' ', '_')}"
        
        # JSON format
        json_content = formatter.format_output(output, "json")
        json_file = output_dir / f"{base_name}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(json_content)
        
        # HTML format
        html_content = formatter.format_output(output, "html")
        html_file = output_dir / f"{base_name}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ Saved {output.metadata.agent_role} output:")
        print(f"   📄 {json_file}")
        print(f"   🌐 {html_file}")
    
    # Save consolidated report
    consolidated_html = formatter.format_multiple_outputs(
        workflow_result.outputs,
        "html",
        aggregate=True,
        custom_options={"title": "Complete Workflow Report"}
    )
    
    report_file = output_dir / "complete_workflow_report.html"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(consolidated_html)
    
    print(f"\n📊 Complete Workflow Report: {report_file}")
    
    # Save analytics as JSON
    analytics_file = output_dir / "workflow_analytics.json"
    with open(analytics_file, "w", encoding="utf-8") as f:
        import json
        json.dump({
            "summary": workflow_result.summary,
            "analytics": workflow_result.analytics,
            "insights": workflow_result.insights
        }, f, indent=2, default=str)
    
    print(f"📈 Workflow Analytics: {analytics_file}")
    
    print(f"\n✅ All sample outputs saved to: {output_dir.absolute()}")


def main():
    """Main demonstration function."""
    print("🚀 CrewAI Output Management System Demo")
    print("=" * 50)
    print("This demo shows how to properly structure agent outputs")
    print("for consistent, validated, and well-formatted results.\n")
    
    try:
        # Run all demonstrations
        save_sample_outputs()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\nThe output management system provides:")
        print("• Structured data models for consistent outputs")
        print("• Comprehensive validation with custom rules")
        print("• Multiple format support (JSON, HTML, Markdown, etc.)")
        print("• Workflow analytics and insights")
        print("• Result aggregation and consolidation")
        print("• Quality scoring and ranking")
        
        print(f"\n📁 Check the generated files:")
        print("   • workflow_report.md - Markdown report")
        print("   • sample_outputs/ - Individual and consolidated outputs")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 