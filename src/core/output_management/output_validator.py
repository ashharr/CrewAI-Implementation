"""
Output Validator for CrewAI Agent Results

Validates agent outputs against schemas, quality standards, and business rules
to ensure outputs meet requirements and maintain consistency.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime

from .structured_output import (
    StructuredOutput, 
    OutputValidation, 
    OutputSchema,
    OutputType,
    OutputStatus
)


class ValidationRule:
    """A single validation rule with criteria and error handling."""
    
    def __init__(
        self,
        name: str,
        description: str,
        validator_func: Callable[[StructuredOutput], bool],
        error_message: str,
        warning_only: bool = False,
        weight: float = 1.0
    ):
        self.name = name
        self.description = description
        self.validator_func = validator_func
        self.error_message = error_message
        self.warning_only = warning_only
        self.weight = weight
    
    def validate(self, output: StructuredOutput) -> tuple[bool, str]:
        """
        Validate an output against this rule.
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            is_valid = self.validator_func(output)
            return is_valid, "" if is_valid else self.error_message
        except Exception as e:
            return False, f"Validation error in {self.name}: {str(e)}"


class OutputValidator:
    """
    Validates structured outputs against various criteria including
    schemas, quality standards, and business rules.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.custom_rules: List[ValidationRule] = []
        self.built_in_rules = self._create_built_in_rules()
    
    def validate_output(
        self,
        output: StructuredOutput,
        schema: Optional[OutputSchema] = None,
        custom_rules: Optional[List[ValidationRule]] = None,
        strict_mode: bool = False
    ) -> OutputValidation:
        """
        Validate a structured output against schema and rules.
        
        Args:
            output: Output to validate
            schema: Optional schema to validate against
            custom_rules: Additional validation rules
            strict_mode: Whether to treat warnings as errors
            
        Returns:
            OutputValidation with detailed results
        """
        errors = []
        warnings = []
        requirements_met = {}
        
        # Schema validation
        if schema:
            schema_validation = schema.validate_output(output)
            errors.extend(schema_validation.errors)
            warnings.extend(schema_validation.warnings)
            requirements_met.update(schema_validation.requirements_met)
        
        # Built-in rule validation
        for rule in self.built_in_rules:
            is_valid, message = rule.validate(output)
            if not is_valid:
                if rule.warning_only and not strict_mode:
                    warnings.append(f"{rule.name}: {message}")
                else:
                    errors.append(f"{rule.name}: {message}")
                requirements_met[rule.name] = False
            else:
                requirements_met[rule.name] = True
        
        # Custom rule validation
        rules_to_check = custom_rules or self.custom_rules
        for rule in rules_to_check:
            is_valid, message = rule.validate(output)
            if not is_valid:
                if rule.warning_only and not strict_mode:
                    warnings.append(f"{rule.name}: {message}")
                else:
                    errors.append(f"{rule.name}: {message}")
                requirements_met[rule.name] = False
            else:
                requirements_met[rule.name] = True
        
        # Calculate validation score
        total_requirements = len(requirements_met)
        if total_requirements > 0:
            # Weight the score by rule importance
            weighted_score = 0.0
            total_weight = 0.0
            
            for rule_name, met in requirements_met.items():
                # Find rule weight (default to 1.0)
                weight = 1.0
                for rule in self.built_in_rules + rules_to_check:
                    if rule.name == rule_name:
                        weight = rule.weight
                        break
                
                if met:
                    weighted_score += weight
                total_weight += weight
            
            validation_score = weighted_score / total_weight if total_weight > 0 else 0.0
        else:
            validation_score = 1.0  # No requirements means perfect score
        
        # Determine overall validity
        is_valid = len(errors) == 0
        
        return OutputValidation(
            is_valid=is_valid,
            validation_score=validation_score,
            errors=errors,
            warnings=warnings,
            requirements_met=requirements_met
        )
    
    def add_custom_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        self.custom_rules.append(rule)
        self.logger.info(f"Added custom validation rule: {rule.name}")
    
    def remove_custom_rule(self, rule_name: str) -> bool:
        """Remove a custom validation rule by name."""
        for i, rule in enumerate(self.custom_rules):
            if rule.name == rule_name:
                del self.custom_rules[i]
                self.logger.info(f"Removed custom validation rule: {rule_name}")
                return True
        return False
    
    def validate_multiple_outputs(
        self,
        outputs: List[StructuredOutput],
        schema: Optional[OutputSchema] = None,
        custom_rules: Optional[List[ValidationRule]] = None,
        strict_mode: bool = False
    ) -> List[OutputValidation]:
        """Validate multiple outputs and return list of validations."""
        validations = []
        
        for output in outputs:
            validation = self.validate_output(output, schema, custom_rules, strict_mode)
            validations.append(validation)
        
        return validations
    
    def get_validation_summary(
        self,
        validations: List[OutputValidation]
    ) -> Dict[str, Any]:
        """
        Generate a summary of multiple validation results.
        
        Args:
            validations: List of validation results
            
        Returns:
            Summary statistics
        """
        total_validations = len(validations)
        if total_validations == 0:
            return {"error": "No validations to summarize"}
        
        valid_count = sum(1 for v in validations if v.is_valid)
        total_errors = sum(len(v.errors) for v in validations)
        total_warnings = sum(len(v.warnings) for v in validations)
        
        scores = [v.validation_score for v in validations]
        avg_score = sum(scores) / len(scores)
        
        return {
            "total_validations": total_validations,
            "valid_count": valid_count,
            "invalid_count": total_validations - valid_count,
            "success_rate": valid_count / total_validations,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "avg_validation_score": avg_score,
            "min_score": min(scores),
            "max_score": max(scores)
        }
    
    def _create_built_in_rules(self) -> List[ValidationRule]:
        """Create built-in validation rules."""
        rules = []
        
        # Content existence rule
        rules.append(ValidationRule(
            name="content_exists",
            description="Output must have content",
            validator_func=lambda output: output.content is not None and str(output.content).strip() != "",
            error_message="Output has no content or empty content",
            weight=2.0
        ))
        
        # Minimum content length rule
        rules.append(ValidationRule(
            name="minimum_content_length",
            description="Content must meet minimum length requirements",
            validator_func=lambda output: len(str(output.content)) >= 10,
            error_message="Content is too short (less than 10 characters)",
            warning_only=True,
            weight=1.0
        ))
        
        # Status consistency rule
        rules.append(ValidationRule(
            name="status_consistency",
            description="Status should match validation results",
            validator_func=lambda output: not (output.status == OutputStatus.SUCCESS and output.error_details),
            error_message="Status is SUCCESS but error details are present",
            weight=1.5
        ))
        
        # Metadata completeness rule
        rules.append(ValidationRule(
            name="metadata_completeness",
            description="Essential metadata fields should be present",
            validator_func=lambda output: (
                output.metadata.agent_id and 
                output.metadata.agent_role and 
                output.metadata.timestamp
            ),
            error_message="Missing essential metadata fields (agent_id, agent_role, or timestamp)",
            weight=1.5
        ))
        
        # Content type consistency rule
        rules.append(ValidationRule(
            name="content_type_consistency",
            description="Content should match declared output type",
            validator_func=self._validate_content_type_consistency,
            error_message="Content does not match declared output type",
            warning_only=True,
            weight=1.0
        ))
        
        # Word count reasonableness rule
        rules.append(ValidationRule(
            name="word_count_accuracy",
            description="Word count metadata should be accurate",
            validator_func=self._validate_word_count_accuracy,
            error_message="Word count metadata significantly differs from actual content",
            warning_only=True,
            weight=0.5
        ))
        
        # No suspicious content rule
        rules.append(ValidationRule(
            name="no_suspicious_content",
            description="Content should not contain suspicious patterns",
            validator_func=self._validate_no_suspicious_content,
            error_message="Content contains suspicious patterns",
            weight=2.0
        ))
        
        # Proper encoding rule
        rules.append(ValidationRule(
            name="proper_encoding",
            description="Content should be properly encoded",
            validator_func=self._validate_proper_encoding,
            error_message="Content has encoding issues",
            weight=1.0
        ))
        
        # JSON validity rule (for JSON outputs)
        rules.append(ValidationRule(
            name="json_validity",
            description="JSON outputs should be valid JSON",
            validator_func=self._validate_json_validity,
            error_message="JSON content is not valid JSON",
            weight=2.0
        ))
        
        # Markdown structure rule (for Markdown outputs)
        rules.append(ValidationRule(
            name="markdown_structure",
            description="Markdown outputs should have proper structure",
            validator_func=self._validate_markdown_structure,
            error_message="Markdown content has structural issues",
            warning_only=True,
            weight=0.5
        ))
        
        return rules
    
    def _validate_content_type_consistency(self, output: StructuredOutput) -> bool:
        """Validate that content matches the declared output type."""
        content_str = str(output.content)
        
        if output.output_type == OutputType.JSON:
            try:
                import json
                if isinstance(output.content, (dict, list)):
                    return True
                json.loads(content_str)
                return True
            except:
                return False
        
        elif output.output_type == OutputType.MARKDOWN:
            # Check for basic markdown patterns
            markdown_patterns = [r'^#{1,6}\s', r'\*\*.*?\*\*', r'\*.*?\*', r'^\s*[-*+]\s']
            return any(re.search(pattern, content_str, re.MULTILINE) for pattern in markdown_patterns)
        
        elif output.output_type == OutputType.HTML:
            return bool(re.search(r'<[^>]+>', content_str))
        
        elif output.output_type == OutputType.CSV:
            lines = content_str.strip().split('\n')
            if len(lines) < 2:
                return False
            return all(',' in line for line in lines[:3])
        
        # For TEXT type, any content is acceptable
        return True
    
    def _validate_word_count_accuracy(self, output: StructuredOutput) -> bool:
        """Validate that word count metadata is reasonably accurate."""
        if not output.metadata.word_count:
            return True  # No word count to validate
        
        actual_words = len(str(output.content).split())
        reported_words = output.metadata.word_count
        
        # Allow 10% variance
        variance = abs(actual_words - reported_words) / max(actual_words, 1)
        return variance <= 0.1
    
    def _validate_no_suspicious_content(self, output: StructuredOutput) -> bool:
        """Check for suspicious or problematic content patterns."""
        content_str = str(output.content).lower()
        
        suspicious_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',    # JavaScript URLs
            r'eval\s*\(',      # Eval functions
            r'exec\s*\(',      # Exec functions
            r'system\s*\(',    # System calls
            r'rm\s+-rf',       # Dangerous shell commands
            r'format\s+c:',    # Format commands
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content_str, re.IGNORECASE):
                return False
        
        return True
    
    def _validate_proper_encoding(self, output: StructuredOutput) -> bool:
        """Check for encoding issues in content."""
        try:
            content_str = str(output.content)
            # Try to encode/decode to check for issues
            content_str.encode('utf-8').decode('utf-8')
            
            # Check for common encoding artifacts
            encoding_artifacts = ['�', '\ufffd', '\x00']
            return not any(artifact in content_str for artifact in encoding_artifacts)
        except:
            return False
    
    def _validate_json_validity(self, output: StructuredOutput) -> bool:
        """Validate JSON outputs are valid JSON."""
        if output.output_type != OutputType.JSON:
            return True  # Not applicable to non-JSON outputs
        
        try:
            import json
            if isinstance(output.content, (dict, list)):
                # Already parsed, try to serialize
                json.dumps(output.content)
                return True
            else:
                # String content, try to parse
                json.loads(str(output.content))
                return True
        except:
            return False
    
    def _validate_markdown_structure(self, output: StructuredOutput) -> bool:
        """Validate basic Markdown structure."""
        if output.output_type != OutputType.MARKDOWN:
            return True  # Not applicable to non-Markdown outputs
        
        content_str = str(output.content)
        
        # Check for balanced formatting
        bold_markers = content_str.count('**')
        italic_markers = content_str.count('*') - bold_markers * 2
        
        # Bold markers should be even (opening and closing)
        if bold_markers % 2 != 0:
            return False
        
        # Check for properly formed headers
        lines = content_str.split('\n')
        for line in lines:
            if line.startswith('#'):
                # Header should have space after #
                if not re.match(r'^#{1,6}\s+', line):
                    return False
        
        return True
    
    def create_content_quality_rule(
        self,
        min_word_count: Optional[int] = None,
        max_word_count: Optional[int] = None,
        required_keywords: Optional[List[str]] = None,
        forbidden_words: Optional[List[str]] = None
    ) -> ValidationRule:
        """
        Create a content quality validation rule.
        
        Args:
            min_word_count: Minimum required words
            max_word_count: Maximum allowed words
            required_keywords: Keywords that must be present
            forbidden_words: Words that should not be present
            
        Returns:
            ValidationRule for content quality
        """
        def validate_content_quality(output: StructuredOutput) -> bool:
            content_str = str(output.content).lower()
            word_count = len(content_str.split())
            
            # Check word count limits
            if min_word_count and word_count < min_word_count:
                return False
            if max_word_count and word_count > max_word_count:
                return False
            
            # Check required keywords
            if required_keywords:
                for keyword in required_keywords:
                    if keyword.lower() not in content_str:
                        return False
            
            # Check forbidden words
            if forbidden_words:
                for word in forbidden_words:
                    if word.lower() in content_str:
                        return False
            
            return True
        
        return ValidationRule(
            name="content_quality",
            description="Content quality standards",
            validator_func=validate_content_quality,
            error_message="Content does not meet quality standards",
            weight=1.5
        )
    
    def create_business_rule(
        self,
        name: str,
        description: str,
        validator_func: Callable[[StructuredOutput], bool],
        error_message: str,
        warning_only: bool = False
    ) -> ValidationRule:
        """
        Create a custom business rule.
        
        Args:
            name: Rule name
            description: Rule description
            validator_func: Function that validates the output
            error_message: Message for validation failures
            warning_only: Whether failures are warnings only
            
        Returns:
            ValidationRule for the business logic
        """
        return ValidationRule(
            name=name,
            description=description,
            validator_func=validator_func,
            error_message=error_message,
            warning_only=warning_only,
            weight=1.0
        ) 