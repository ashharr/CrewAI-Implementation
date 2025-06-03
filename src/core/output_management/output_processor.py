"""
Output Processor for CrewAI Agent Results

Processes raw agent outputs into structured formats, extracts metadata,
and handles different content types and formats.
"""

import re
import json
import yaml
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging

from .structured_output import (
    StructuredOutput, 
    OutputMetadata, 
    OutputType, 
    OutputStatus,
    OutputSchema
)


class OutputProcessor:
    """
    Processes raw agent outputs into structured formats.
    
    Handles parsing, metadata extraction, content organization,
    and format conversion for different output types.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def process_agent_output(
        self, 
        raw_output: Any,
        agent_id: str,
        agent_role: str,
        task_id: Optional[str] = None,
        task_name: Optional[str] = None,
        workflow_id: Optional[str] = None,
        execution_time: Optional[float] = None,
        schema: Optional[OutputSchema] = None
    ) -> StructuredOutput:
        """
        Process raw agent output into structured format.
        
        Args:
            raw_output: Raw output from agent
            agent_id: ID of the agent
            agent_role: Role of the agent
            task_id: Optional task ID
            task_name: Optional task name
            workflow_id: Optional workflow ID
            execution_time: Optional execution time
            schema: Optional schema for validation
            
        Returns:
            StructuredOutput: Processed and structured output
        """
        try:
            # Determine output type and extract content
            output_type, content = self._determine_output_type(raw_output)
            
            # Extract metadata from content
            metadata = self._extract_metadata(
                content, agent_id, agent_role, task_id, 
                task_name, workflow_id, execution_time
            )
            
            # Organize content into sections
            sections = self._organize_content_sections(content, output_type)
            
            # Extract tags and keywords
            tags = self._extract_tags(content)
            keywords = self._extract_keywords(content)
            
            # Create structured output
            structured_output = StructuredOutput(
                content=content,
                output_type=output_type,
                status=OutputStatus.SUCCESS,
                metadata=metadata,
                sections=sections,
                tags=tags,
                keywords=keywords
            )
            
            # Validate against schema if provided
            if schema:
                validation = schema.validate_output(structured_output)
                structured_output.validation = validation
                
                # Update status based on validation
                if not validation.is_valid:
                    structured_output.status = OutputStatus.PARTIAL
                    structured_output.processing_notes.append(
                        f"Validation failed with {len(validation.errors)} errors"
                    )
            
            self.logger.info(f"Successfully processed output from {agent_role}")
            return structured_output
            
        except Exception as e:
            self.logger.error(f"Error processing agent output: {e}")
            
            # Return failed output with error details
            return StructuredOutput(
                content=str(raw_output),
                output_type=OutputType.TEXT,
                status=OutputStatus.FAILED,
                metadata=OutputMetadata(
                    agent_id=agent_id,
                    agent_role=agent_role,
                    task_id=task_id,
                    task_name=task_name,
                    workflow_id=workflow_id,
                    execution_time=execution_time
                ),
                error_details=str(e)
            )
    
    def _determine_output_type(self, raw_output: Any) -> Tuple[OutputType, Union[str, Dict, List]]:
        """Determine the output type and extract content."""
        
        if isinstance(raw_output, dict):
            return OutputType.JSON, raw_output
        elif isinstance(raw_output, list):
            return OutputType.JSON, raw_output
        elif isinstance(raw_output, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(raw_output)
                return OutputType.JSON, parsed
            except json.JSONDecodeError:
                pass
            
            # Check for YAML
            try:
                parsed = yaml.safe_load(raw_output)
                if isinstance(parsed, (dict, list)):
                    return OutputType.YAML, parsed
            except yaml.YAMLError:
                pass
            
            # Check for Markdown
            if self._is_markdown(raw_output):
                return OutputType.MARKDOWN, raw_output
            
            # Check for HTML
            if self._is_html(raw_output):
                return OutputType.HTML, raw_output
            
            # Check for CSV
            if self._is_csv(raw_output):
                return OutputType.CSV, raw_output
            
            # Default to text
            return OutputType.TEXT, raw_output
        else:
            # Convert to string for unknown types
            return OutputType.TEXT, str(raw_output)
    
    def _is_markdown(self, content: str) -> bool:
        """Check if content appears to be Markdown."""
        markdown_patterns = [
            r'^#{1,6}\s+',  # Headers
            r'\*\*.*?\*\*',  # Bold
            r'\*.*?\*',      # Italic
            r'^\s*[\-\*\+]\s+',  # Lists
            r'^\s*\d+\.\s+',     # Numbered lists
            r'\[.*?\]\(.*?\)',   # Links
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False
    
    def _is_html(self, content: str) -> bool:
        """Check if content appears to be HTML."""
        html_pattern = r'<[^>]+>'
        return bool(re.search(html_pattern, content))
    
    def _is_csv(self, content: str) -> bool:
        """Check if content appears to be CSV."""
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return False
        
        # Check if first few lines have consistent comma separation
        separators = [line.count(',') for line in lines[:3]]
        return len(set(separators)) == 1 and separators[0] > 0
    
    def _extract_metadata(
        self, 
        content: Union[str, Dict, List],
        agent_id: str,
        agent_role: str,
        task_id: Optional[str],
        task_name: Optional[str],
        workflow_id: Optional[str],
        execution_time: Optional[float]
    ) -> OutputMetadata:
        """Extract metadata from content and parameters."""
        
        # Calculate word count
        word_count = self._calculate_word_count(content)
        
        # Extract source count from content
        source_count = self._count_sources(content)
        
        # Try to extract confidence indicators
        confidence_score = self._extract_confidence_score(content)
        
        return OutputMetadata(
            agent_id=agent_id,
            agent_role=agent_role,
            task_id=task_id,
            task_name=task_name,
            workflow_id=workflow_id,
            execution_time=execution_time,
            word_count=word_count,
            source_count=source_count,
            confidence_score=confidence_score
        )
    
    def _calculate_word_count(self, content: Union[str, Dict, List]) -> int:
        """Calculate word count from content."""
        if isinstance(content, str):
            # Remove markdown/html tags for accurate count
            clean_text = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
            clean_text = re.sub(r'\[.*?\]\(.*?\)', '', clean_text)  # Remove markdown links
            clean_text = re.sub(r'[#*_`]', '', clean_text)  # Remove markdown formatting
            words = clean_text.split()
            return len(words)
        elif isinstance(content, dict):
            # Count words in all string values
            total_words = 0
            for value in content.values():
                if isinstance(value, str):
                    total_words += len(value.split())
            return total_words
        elif isinstance(content, list):
            # Count words in all string items
            total_words = 0
            for item in content:
                if isinstance(item, str):
                    total_words += len(item.split())
            return total_words
        return 0
    
    def _count_sources(self, content: Union[str, Dict, List]) -> Optional[int]:
        """Count sources/citations in content."""
        if isinstance(content, str):
            # Look for common citation patterns
            patterns = [
                r'\[.*?\]\(https?://.*?\)',  # Markdown links
                r'https?://[^\s]+',          # URLs
                r'\(Source:.*?\)',           # Source citations
                r'\[Source:.*?\]',           # Bracketed sources
                r'Source:|\*Source\*',       # Source labels
            ]
            
            sources = set()
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                sources.update(matches)
            
            return len(sources) if sources else None
        
        elif isinstance(content, dict):
            # Look for sources in dict values
            if 'sources' in content:
                sources_value = content['sources']
                if isinstance(sources_value, list):
                    return len(sources_value)
                elif isinstance(sources_value, str):
                    return len(sources_value.split('\n'))
            
            # Count sources in all text values
            total_sources = 0
            for value in content.values():
                if isinstance(value, str):
                    count = self._count_sources(value)
                    if count:
                        total_sources += count
            return total_sources if total_sources > 0 else None
        
        return None
    
    def _extract_confidence_score(self, content: Union[str, Dict, List]) -> Optional[float]:
        """Extract confidence score from content if available."""
        if isinstance(content, dict):
            # Look for confidence keys
            confidence_keys = ['confidence', 'confidence_score', 'certainty', 'quality_score']
            for key in confidence_keys:
                if key in content:
                    value = content[key]
                    if isinstance(value, (int, float)):
                        return min(max(float(value), 0.0), 1.0)
        
        elif isinstance(content, str):
            # Look for confidence patterns in text
            patterns = [
                r'confidence[:\s]+([0-9.]+)',
                r'certainty[:\s]+([0-9.]+)',
                r'quality[:\s]+([0-9.]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    try:
                        score = float(match.group(1))
                        return min(max(score, 0.0), 1.0)
                    except ValueError:
                        continue
        
        return None
    
    def _organize_content_sections(
        self, 
        content: Union[str, Dict, List], 
        output_type: OutputType
    ) -> Optional[Dict[str, Any]]:
        """Organize content into logical sections."""
        
        if output_type == OutputType.MARKDOWN and isinstance(content, str):
            return self._parse_markdown_sections(content)
        elif output_type == OutputType.JSON and isinstance(content, dict):
            return content  # Already structured
        elif isinstance(content, str):
            return self._parse_text_sections(content)
        
        return None
    
    def _parse_markdown_sections(self, content: str) -> Dict[str, Any]:
        """Parse Markdown content into sections."""
        sections = {}
        current_section = "introduction"
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if header_match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                level = len(header_match.group(1))
                section_title = header_match.group(2).lower().replace(' ', '_')
                current_section = section_title
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _parse_text_sections(self, content: str) -> Dict[str, Any]:
        """Parse plain text into sections based on common patterns."""
        sections = {}
        
        # Look for common section patterns
        section_patterns = [
            (r'^(summary|executive summary)[:\n]', 'summary'),
            (r'^(introduction|intro)[:\n]', 'introduction'),
            (r'^(findings|key findings)[:\n]', 'findings'),
            (r'^(analysis|detailed analysis)[:\n]', 'analysis'),
            (r'^(recommendations?)[:\n]', 'recommendations'),
            (r'^(conclusion|conclusions?)[:\n]', 'conclusion'),
            (r'^(sources?|references?)[:\n]', 'sources'),
        ]
        
        lines = content.split('\n')
        current_section = "content"
        current_content = []
        
        for line in lines:
            section_found = False
            for pattern, section_name in section_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_tags(self, content: Union[str, Dict, List]) -> List[str]:
        """Extract tags from content."""
        tags = []
        
        if isinstance(content, dict):
            # Look for explicit tags
            if 'tags' in content:
                tags_value = content['tags']
                if isinstance(tags_value, list):
                    tags.extend(tags_value)
                elif isinstance(tags_value, str):
                    tags.extend([tag.strip() for tag in tags_value.split(',')])
        
        elif isinstance(content, str):
            # Look for hashtags
            hashtag_pattern = r'#(\w+)'
            hashtags = re.findall(hashtag_pattern, content)
            tags.extend(hashtags)
            
            # Look for explicit tag sections
            tag_pattern = r'tags?[:\s]+([^\n]+)'
            tag_matches = re.findall(tag_pattern, content, re.IGNORECASE)
            for match in tag_matches:
                tag_list = [tag.strip() for tag in match.split(',')]
                tags.extend(tag_list)
        
        # Clean and deduplicate tags
        cleaned_tags = list(set([tag.lower().strip('#') for tag in tags if tag.strip()]))
        return cleaned_tags[:10]  # Limit to 10 tags
    
    def _extract_keywords(self, content: Union[str, Dict, List]) -> List[str]:
        """Extract keywords from content."""
        keywords = []
        
        if isinstance(content, dict):
            # Look for explicit keywords
            if 'keywords' in content:
                keywords_value = content['keywords']
                if isinstance(keywords_value, list):
                    keywords.extend(keywords_value)
                elif isinstance(keywords_value, str):
                    keywords.extend([kw.strip() for kw in keywords_value.split(',')])
        
        elif isinstance(content, str):
            # Look for keyword sections
            keyword_pattern = r'keywords?[:\s]+([^\n]+)'
            keyword_matches = re.findall(keyword_pattern, content, re.IGNORECASE)
            for match in keyword_matches:
                keyword_list = [kw.strip() for kw in match.split(',')]
                keywords.extend(keyword_list)
            
            # Extract important terms (simplified approach)
            # In a real implementation, you might use NLP libraries
            words = re.findall(r'\b[A-Z][a-z]+\b', content)  # Capitalized words
            keywords.extend(words)
        
        # Clean and deduplicate keywords
        cleaned_keywords = list(set([kw.lower().strip() for kw in keywords if kw.strip()]))
        return cleaned_keywords[:15]  # Limit to 15 keywords
    
    def process_crew_output(
        self, 
        crew_result: Any,
        workflow_id: Optional[str] = None
    ) -> List[StructuredOutput]:
        """
        Process the complete result from a crew execution.
        
        Args:
            crew_result: Result from crew.kickoff()
            workflow_id: Optional workflow ID
            
        Returns:
            List of structured outputs from each agent/task
        """
        structured_outputs = []
        
        try:
            # Handle different crew result formats
            if hasattr(crew_result, 'tasks_output'):
                # CrewAI's task outputs
                for i, task_output in enumerate(crew_result.tasks_output):
                    structured = self.process_agent_output(
                        raw_output=task_output.raw,
                        agent_id=f"agent_{i}",
                        agent_role=getattr(task_output, 'agent', {}).get('role', 'Unknown'),
                        task_id=f"task_{i}",
                        workflow_id=workflow_id
                    )
                    structured_outputs.append(structured)
            
            elif isinstance(crew_result, list):
                # List of outputs
                for i, output in enumerate(crew_result):
                    structured = self.process_agent_output(
                        raw_output=output,
                        agent_id=f"agent_{i}",
                        agent_role="Unknown",
                        task_id=f"task_{i}",
                        workflow_id=workflow_id
                    )
                    structured_outputs.append(structured)
            
            else:
                # Single output
                structured = self.process_agent_output(
                    raw_output=crew_result,
                    agent_id="agent_0",
                    agent_role="Unknown",
                    workflow_id=workflow_id
                )
                structured_outputs.append(structured)
        
        except Exception as e:
            self.logger.error(f"Error processing crew output: {e}")
            # Return error output
            error_output = StructuredOutput(
                content=str(crew_result),
                output_type=OutputType.TEXT,
                status=OutputStatus.FAILED,
                metadata=OutputMetadata(
                    agent_id="unknown",
                    agent_role="Unknown",
                    workflow_id=workflow_id
                ),
                error_details=str(e)
            )
            structured_outputs.append(error_output)
        
        return structured_outputs 