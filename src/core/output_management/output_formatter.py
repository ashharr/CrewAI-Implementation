"""
Output Formatter for CrewAI Structured Outputs

Converts structured outputs to various formats for different consumption
needs including JSON, HTML, PDF, CSV, and custom templates.
"""

import json
import csv
import io
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

from .structured_output import StructuredOutput, OutputType


class OutputFormatter:
    """
    Formats structured outputs into various target formats.
    
    Supports JSON, HTML, PDF, CSV, Markdown, and custom template-based formats.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.template_dir = template_dir
        
        # Set up Jinja2 environment for templating
        if template_dir and Path(template_dir).exists():
            self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.jinja_env = Environment(loader=FileSystemLoader('.'))
    
    def format_output(
        self, 
        output: StructuredOutput, 
        target_format: str,
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Union[str, bytes]:
        """
        Format a structured output to the target format.
        
        Args:
            output: Structured output to format
            target_format: Target format (json, html, pdf, csv, markdown, template)
            template_name: Template name for custom formatting
            custom_options: Additional formatting options
            
        Returns:
            Formatted output as string or bytes
        """
        options = custom_options or {}
        
        try:
            if target_format.lower() == 'json':
                return self._format_as_json(output, options)
            elif target_format.lower() == 'html':
                return self._format_as_html(output, options)
            elif target_format.lower() == 'markdown':
                return self._format_as_markdown(output, options)
            elif target_format.lower() == 'csv':
                return self._format_as_csv(output, options)
            elif target_format.lower() == 'xml':
                return self._format_as_xml(output, options)
            elif target_format.lower() == 'template':
                if not template_name:
                    raise ValueError("Template name required for template format")
                return self._format_with_template(output, template_name, options)
            elif target_format.lower() == 'summary':
                return self._format_as_summary(output, options)
            else:
                raise ValueError(f"Unsupported format: {target_format}")
                
        except Exception as e:
            self.logger.error(f"Error formatting output: {e}")
            return f"Error formatting output: {str(e)}"
    
    def format_multiple_outputs(
        self,
        outputs: List[StructuredOutput],
        target_format: str,
        aggregate: bool = True,
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Union[str, bytes]:
        """
        Format multiple structured outputs.
        
        Args:
            outputs: List of structured outputs
            target_format: Target format
            aggregate: Whether to aggregate into single document
            template_name: Template name for custom formatting
            custom_options: Additional formatting options
            
        Returns:
            Formatted output as string or bytes
        """
        options = custom_options or {}
        
        if not aggregate:
            # Format each output separately
            formatted_outputs = []
            for i, output in enumerate(outputs):
                formatted = self.format_output(output, target_format, template_name, options)
                formatted_outputs.append(f"=== Output {i+1} ===\n{formatted}\n")
            return "\n".join(formatted_outputs)
        
        # Aggregate outputs based on format
        try:
            if target_format.lower() == 'json':
                return self._format_multiple_as_json(outputs, options)
            elif target_format.lower() == 'html':
                return self._format_multiple_as_html(outputs, options)
            elif target_format.lower() == 'markdown':
                return self._format_multiple_as_markdown(outputs, options)
            elif target_format.lower() == 'summary':
                return self._format_multiple_as_summary(outputs, options)
            else:
                # Default: format each separately
                return self.format_multiple_outputs(outputs, target_format, False, template_name, options)
                
        except Exception as e:
            self.logger.error(f"Error formatting multiple outputs: {e}")
            return f"Error formatting outputs: {str(e)}"
    
    def _format_as_json(self, output: StructuredOutput, options: Dict[str, Any]) -> str:
        """Format output as JSON."""
        indent = options.get('indent', 2)
        include_metadata = options.get('include_metadata', True)
        
        if include_metadata:
            return output.to_json(indent=indent)
        else:
            # Return only content
            return json.dumps(output.content, indent=indent, default=str)
    
    def _format_as_html(self, output: StructuredOutput, options: Dict[str, Any]) -> str:
        """Format output as HTML."""
        include_css = options.get('include_css', True)
        include_metadata = options.get('include_metadata', True)
        
        html_parts = []
        
        # Add CSS if requested
        if include_css:
            html_parts.append(self._get_default_css())
        
        html_parts.append('<div class="crew-output">')
        
        # Add metadata section
        if include_metadata:
            html_parts.append(self._format_metadata_as_html(output))
        
        # Add content based on type
        if output.output_type == OutputType.MARKDOWN:
            # Convert markdown to HTML (simplified)
            html_content = self._markdown_to_html(str(output.content))
        elif output.output_type == OutputType.HTML:
            html_content = str(output.content)
        elif output.output_type == OutputType.JSON:
            html_content = f'<pre class="json-content">{json.dumps(output.content, indent=2)}</pre>'
        else:
            html_content = f'<div class="text-content">{self._escape_html(str(output.content))}</div>'
        
        html_parts.append(f'<div class="content">{html_content}</div>')
        
        # Add sections if available
        if output.sections:
            html_parts.append('<div class="sections">')
            for section_name, section_content in output.sections.items():
                html_parts.append(f'<div class="section" data-section="{section_name}">')
                html_parts.append(f'<h3>{section_name.replace("_", " ").title()}</h3>')
                html_parts.append(f'<div class="section-content">{self._escape_html(str(section_content))}</div>')
                html_parts.append('</div>')
            html_parts.append('</div>')
        
        # Add validation info if available
        if output.validation:
            html_parts.append(self._format_validation_as_html(output.validation))
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _format_as_markdown(self, output: StructuredOutput, options: Dict[str, Any]) -> str:
        """Format output as Markdown."""
        include_metadata = options.get('include_metadata', True)
        
        md_parts = []
        
        # Add title
        title = options.get('title', f"Output from {output.metadata.agent_role}")
        md_parts.append(f"# {title}\n")
        
        # Add metadata
        if include_metadata:
            md_parts.append("## Metadata\n")
            md_parts.append(f"- **Agent**: {output.metadata.agent_role}")
            md_parts.append(f"- **Status**: {output.status}")
            md_parts.append(f"- **Type**: {output.output_type}")
            md_parts.append(f"- **Timestamp**: {output.metadata.timestamp}")
            if output.metadata.word_count:
                md_parts.append(f"- **Word Count**: {output.metadata.word_count}")
            if output.metadata.execution_time:
                md_parts.append(f"- **Execution Time**: {output.metadata.execution_time:.2f}s")
            md_parts.append("")
        
        # Add content
        md_parts.append("## Content\n")
        if output.output_type == OutputType.MARKDOWN:
            md_parts.append(str(output.content))
        elif output.output_type == OutputType.JSON:
            md_parts.append("```json")
            md_parts.append(json.dumps(output.content, indent=2))
            md_parts.append("```")
        else:
            md_parts.append(str(output.content))
        
        md_parts.append("")
        
        # Add sections
        if output.sections:
            md_parts.append("## Sections\n")
            for section_name, section_content in output.sections.items():
                md_parts.append(f"### {section_name.replace('_', ' ').title()}\n")
                md_parts.append(str(section_content))
                md_parts.append("")
        
        # Add tags and keywords
        if output.tags:
            md_parts.append(f"**Tags**: {', '.join(output.tags)}")
        if output.keywords:
            md_parts.append(f"**Keywords**: {', '.join(output.keywords)}")
        
        # Add validation info
        if output.validation:
            md_parts.append("\n## Validation\n")
            md_parts.append(f"- **Valid**: {output.validation.is_valid}")
            md_parts.append(f"- **Score**: {output.validation.validation_score:.2f}")
            if output.validation.errors:
                md_parts.append(f"- **Errors**: {len(output.validation.errors)}")
            if output.validation.warnings:
                md_parts.append(f"- **Warnings**: {len(output.validation.warnings)}")
        
        return '\n'.join(md_parts)
    
    def _format_as_csv(self, output: StructuredOutput, options: Dict[str, Any]) -> str:
        """Format output as CSV."""
        output_buffer = io.StringIO()
        writer = csv.writer(output_buffer)
        
        # Write headers
        headers = ['Field', 'Value']
        writer.writerow(headers)
        
        # Write basic info
        writer.writerow(['Agent Role', output.metadata.agent_role])
        writer.writerow(['Status', output.status])
        writer.writerow(['Output Type', output.output_type])
        writer.writerow(['Timestamp', output.metadata.timestamp])
        
        if output.metadata.word_count:
            writer.writerow(['Word Count', output.metadata.word_count])
        if output.metadata.execution_time:
            writer.writerow(['Execution Time', f"{output.metadata.execution_time:.2f}s"])
        
        # Write content (truncated if too long)
        content_str = str(output.content)
        if len(content_str) > 1000:
            content_str = content_str[:1000] + "..."
        writer.writerow(['Content', content_str])
        
        # Write sections
        if output.sections:
            for section_name, section_content in output.sections.items():
                section_str = str(section_content)
                if len(section_str) > 500:
                    section_str = section_str[:500] + "..."
                writer.writerow([f'Section: {section_name}', section_str])
        
        return output_buffer.getvalue()
    
    def _format_as_xml(self, output: StructuredOutput, options: Dict[str, Any]) -> str:
        """Format output as XML."""
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<CrewOutput>')
        
        # Metadata
        xml_parts.append('  <Metadata>')
        xml_parts.append(f'    <AgentRole>{self._escape_xml(output.metadata.agent_role)}</AgentRole>')
        xml_parts.append(f'    <Status>{output.status}</Status>')
        xml_parts.append(f'    <OutputType>{output.output_type}</OutputType>')
        xml_parts.append(f'    <Timestamp>{output.metadata.timestamp}</Timestamp>')
        if output.metadata.word_count:
            xml_parts.append(f'    <WordCount>{output.metadata.word_count}</WordCount>')
        xml_parts.append('  </Metadata>')
        
        # Content
        xml_parts.append('  <Content>')
        if output.output_type == OutputType.JSON:
            xml_parts.append(f'    <JSONData><![CDATA[{json.dumps(output.content)}]]></JSONData>')
        else:
            xml_parts.append(f'    <TextData><![CDATA[{str(output.content)}]]></TextData>')
        xml_parts.append('  </Content>')
        
        # Sections
        if output.sections:
            xml_parts.append('  <Sections>')
            for section_name, section_content in output.sections.items():
                xml_parts.append(f'    <Section name="{self._escape_xml(section_name)}">')
                xml_parts.append(f'      <![CDATA[{str(section_content)}]]>')
                xml_parts.append('    </Section>')
            xml_parts.append('  </Sections>')
        
        xml_parts.append('</CrewOutput>')
        return '\n'.join(xml_parts)
    
    def _format_as_summary(self, output: StructuredOutput, options: Dict[str, Any]) -> str:
        """Format output as a brief summary."""
        summary_parts = []
        
        summary_parts.append(f"Agent: {output.metadata.agent_role}")
        summary_parts.append(f"Status: {output.status}")
        summary_parts.append(f"Time: {output.metadata.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if output.metadata.word_count:
            summary_parts.append(f"Words: {output.metadata.word_count}")
        
        if output.validation:
            summary_parts.append(f"Validation: {output.validation.validation_score:.1%}")
        
        # Content preview
        preview = output.get_content_preview(100)
        summary_parts.append(f"Preview: {preview}")
        
        return " | ".join(summary_parts)
    
    def _format_with_template(
        self, 
        output: StructuredOutput, 
        template_name: str, 
        options: Dict[str, Any]
    ) -> str:
        """Format output using a custom template."""
        try:
            template = self.jinja_env.get_template(template_name)
            
            # Prepare context for template
            context = {
                'output': output,
                'metadata': output.metadata,
                'content': output.content,
                'sections': output.sections,
                'tags': output.tags,
                'keywords': output.keywords,
                'validation': output.validation,
                'options': options,
                'now': datetime.now()
            }
            
            return template.render(**context)
            
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            return f"Template rendering error: {str(e)}"
    
    def _format_multiple_as_json(self, outputs: List[StructuredOutput], options: Dict[str, Any]) -> str:
        """Format multiple outputs as JSON array."""
        output_data = []
        include_metadata = options.get('include_metadata', True)
        
        for output in outputs:
            if include_metadata:
                output_data.append(output.to_dict())
            else:
                output_data.append(output.content)
        
        indent = options.get('indent', 2)
        return json.dumps(output_data, indent=indent, default=str)
    
    def _format_multiple_as_html(self, outputs: List[StructuredOutput], options: Dict[str, Any]) -> str:
        """Format multiple outputs as HTML document."""
        html_parts = []
        
        if options.get('include_css', True):
            html_parts.append(self._get_default_css())
        
        html_parts.append('<div class="crew-outputs">')
        html_parts.append('<h1>Crew Execution Results</h1>')
        
        for i, output in enumerate(outputs):
            html_parts.append(f'<div class="output-item" data-index="{i}">')
            html_parts.append(f'<h2>Output {i+1}: {output.metadata.agent_role}</h2>')
            
            # Format individual output without CSS
            individual_options = {**options, 'include_css': False}
            individual_html = self._format_as_html(output, individual_options)
            html_parts.append(individual_html)
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_multiple_as_markdown(self, outputs: List[StructuredOutput], options: Dict[str, Any]) -> str:
        """Format multiple outputs as Markdown document."""
        md_parts = []
        
        title = options.get('title', 'Crew Execution Results')
        md_parts.append(f"# {title}\n")
        
        # Add execution summary
        md_parts.append("## Execution Summary\n")
        md_parts.append(f"- **Total Outputs**: {len(outputs)}")
        md_parts.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        successful = sum(1 for output in outputs if output.status == "success")
        md_parts.append(f"- **Successful**: {successful}/{len(outputs)}")
        md_parts.append("")
        
        # Add each output
        for i, output in enumerate(outputs):
            md_parts.append(f"## Output {i+1}: {output.metadata.agent_role}\n")
            
            # Format individual output without title
            individual_options = {**options, 'include_metadata': False, 'title': None}
            individual_md = self._format_as_markdown(output, individual_options)
            md_parts.append(individual_md)
            md_parts.append("\n---\n")
        
        return '\n'.join(md_parts)
    
    def _format_multiple_as_summary(self, outputs: List[StructuredOutput], options: Dict[str, Any]) -> str:
        """Format multiple outputs as summary table."""
        summary_parts = []
        
        summary_parts.append("CREW EXECUTION SUMMARY")
        summary_parts.append("=" * 50)
        
        for i, output in enumerate(outputs):
            summary = self._format_as_summary(output, options)
            summary_parts.append(f"{i+1:2d}. {summary}")
        
        summary_parts.append("=" * 50)
        summary_parts.append(f"Total: {len(outputs)} outputs")
        
        return '\n'.join(summary_parts)
    
    # Helper methods
    def _get_default_css(self) -> str:
        """Return default CSS for HTML formatting."""
        return """
        <style>
        .crew-output, .crew-outputs { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .metadata { 
            background: #f5f5f5; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
        .content { 
            line-height: 1.6; 
            margin-bottom: 20px; 
        }
        .sections { 
            margin-top: 20px; 
        }
        .section { 
            border-left: 3px solid #007cba; 
            padding-left: 15px; 
            margin-bottom: 15px; 
        }
        .json-content { 
            background: #f8f8f8; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto; 
        }
        .validation { 
            padding: 10px; 
            border-radius: 5px; 
        }
        .validation.valid { 
            background: #d4edda; 
            border: 1px solid #c3e6cb; 
        }
        .validation.invalid { 
            background: #f8d7da; 
            border: 1px solid #f5c6cb; 
        }
        </style>
        """
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert Markdown to HTML (simplified)."""
        # This is a very basic implementation
        # For production, you'd want to use a proper markdown library
        html = markdown_text
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = html.replace('\n', '<br>\n')
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML entities."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML entities."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))
    
    def _format_metadata_as_html(self, output: StructuredOutput) -> str:
        """Format metadata as HTML."""
        html_parts = ['<div class="metadata">']
        html_parts.append('<h3>Output Metadata</h3>')
        html_parts.append('<ul>')
        html_parts.append(f'<li><strong>Agent:</strong> {output.metadata.agent_role}</li>')
        html_parts.append(f'<li><strong>Status:</strong> {output.status}</li>')
        html_parts.append(f'<li><strong>Type:</strong> {output.output_type}</li>')
        html_parts.append(f'<li><strong>Timestamp:</strong> {output.metadata.timestamp}</li>')
        
        if output.metadata.word_count:
            html_parts.append(f'<li><strong>Word Count:</strong> {output.metadata.word_count}</li>')
        if output.metadata.execution_time:
            html_parts.append(f'<li><strong>Execution Time:</strong> {output.metadata.execution_time:.2f}s</li>')
        
        html_parts.append('</ul>')
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_validation_as_html(self, validation) -> str:
        """Format validation results as HTML."""
        css_class = "valid" if validation.is_valid else "invalid"
        html_parts = [f'<div class="validation {css_class}">']
        html_parts.append('<h3>Validation Results</h3>')
        html_parts.append(f'<p><strong>Valid:</strong> {validation.is_valid}</p>')
        html_parts.append(f'<p><strong>Score:</strong> {validation.validation_score:.1%}</p>')
        
        if validation.errors:
            html_parts.append('<p><strong>Errors:</strong></p>')
            html_parts.append('<ul>')
            for error in validation.errors:
                html_parts.append(f'<li>{self._escape_html(error)}</li>')
            html_parts.append('</ul>')
        
        if validation.warnings:
            html_parts.append('<p><strong>Warnings:</strong></p>')
            html_parts.append('<ul>')
            for warning in validation.warnings:
                html_parts.append(f'<li>{self._escape_html(warning)}</li>')
            html_parts.append('</ul>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts) 