"""
Result Aggregator for CrewAI Workflow Outputs

Combines and aggregates multiple agent outputs into comprehensive
workflow results with analytics, insights, and summary reporting.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from collections import defaultdict, Counter
from statistics import mean, median

from .structured_output import StructuredOutput, OutputStatus, OutputType, OutputMetadata
from .output_formatter import OutputFormatter


class WorkflowResult:
    """Complete result from a workflow execution with aggregated insights."""
    
    def __init__(
        self,
        workflow_id: str,
        workflow_name: str,
        outputs: List[StructuredOutput],
        execution_start: datetime,
        execution_end: datetime
    ):
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.outputs = outputs
        self.execution_start = execution_start
        self.execution_end = execution_end
        self.execution_time = (execution_end - execution_start).total_seconds()
        
        # Calculated properties
        self._analytics = None
        self._summary = None
        self._insights = None
    
    @property
    def analytics(self) -> Dict[str, Any]:
        """Get workflow analytics."""
        if self._analytics is None:
            self._analytics = self._calculate_analytics()
        return self._analytics
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Get workflow summary."""
        if self._summary is None:
            self._summary = self._generate_summary()
        return self._summary
    
    @property
    def insights(self) -> List[str]:
        """Get workflow insights."""
        if self._insights is None:
            self._insights = self._generate_insights()
        return self._insights
    
    def _calculate_analytics(self) -> Dict[str, Any]:
        """Calculate detailed analytics for the workflow."""
        total_outputs = len(self.outputs)
        if total_outputs == 0:
            return {"error": "No outputs to analyze"}
        
        # Status distribution
        status_counts = Counter(output.status for output in self.outputs)
        
        # Agent performance
        agent_performance = defaultdict(list)
        for output in self.outputs:
            agent_performance[output.metadata.agent_role].append(output)
        
        # Content metrics
        word_counts = [output.metadata.word_count for output in self.outputs if output.metadata.word_count]
        execution_times = [output.metadata.execution_time for output in self.outputs if output.metadata.execution_time]
        confidence_scores = [output.metadata.confidence_score for output in self.outputs if output.metadata.confidence_score]
        
        return {
            "total_outputs": total_outputs,
            "status_distribution": dict(status_counts),
            "success_rate": status_counts.get(OutputStatus.SUCCESS, 0) / total_outputs,
            "agent_count": len(agent_performance),
            "agent_performance": {
                agent: {
                    "output_count": len(outputs),
                    "success_rate": sum(1 for o in outputs if o.status == OutputStatus.SUCCESS) / len(outputs),
                    "avg_word_count": mean([o.metadata.word_count for o in outputs if o.metadata.word_count]) if any(o.metadata.word_count for o in outputs) else None,
                    "avg_execution_time": mean([o.metadata.execution_time for o in outputs if o.metadata.execution_time]) if any(o.metadata.execution_time for o in outputs) else None
                }
                for agent, outputs in agent_performance.items()
            },
            "content_metrics": {
                "total_words": sum(word_counts) if word_counts else 0,
                "avg_words_per_output": mean(word_counts) if word_counts else 0,
                "min_words": min(word_counts) if word_counts else 0,
                "max_words": max(word_counts) if word_counts else 0,
                "median_words": median(word_counts) if word_counts else 0
            },
            "performance_metrics": {
                "total_execution_time": self.execution_time,
                "avg_task_time": mean(execution_times) if execution_times else 0,
                "min_task_time": min(execution_times) if execution_times else 0,
                "max_task_time": max(execution_times) if execution_times else 0,
                "avg_confidence": mean(confidence_scores) if confidence_scores else None,
                "min_confidence": min(confidence_scores) if confidence_scores else None,
                "max_confidence": max(confidence_scores) if confidence_scores else None
            },
            "quality_metrics": {
                "outputs_with_validation": sum(1 for o in self.outputs if o.validation),
                "avg_validation_score": mean([o.validation.validation_score for o in self.outputs if o.validation]) if any(o.validation for o in self.outputs) else None,
                "outputs_with_errors": sum(1 for o in self.outputs if o.validation and o.validation.errors),
                "outputs_with_warnings": sum(1 for o in self.outputs if o.validation and o.validation.warnings)
            }
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a workflow summary."""
        analytics = self.analytics
        
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "execution_time": f"{self.execution_time:.2f}s",
            "total_outputs": analytics["total_outputs"],
            "success_rate": f"{analytics['success_rate']:.1%}",
            "total_words": analytics["content_metrics"]["total_words"],
            "agent_count": analytics["agent_count"],
            "started_at": self.execution_start.isoformat(),
            "completed_at": self.execution_end.isoformat(),
            "quality_score": analytics["quality_metrics"]["avg_validation_score"]
        }
    
    def _generate_insights(self) -> List[str]:
        """Generate insights about the workflow execution."""
        insights = []
        analytics = self.analytics
        
        # Performance insights
        if analytics["success_rate"] == 1.0:
            insights.append("🎉 Perfect execution - all outputs completed successfully!")
        elif analytics["success_rate"] >= 0.8:
            insights.append("✅ High success rate - most outputs completed successfully")
        elif analytics["success_rate"] >= 0.5:
            insights.append("⚠️ Moderate success rate - some outputs may need attention")
        else:
            insights.append("❌ Low success rate - workflow may need debugging")
        
        # Content insights
        content_metrics = analytics["content_metrics"]
        if content_metrics["total_words"] > 10000:
            insights.append("📝 High content volume generated")
        elif content_metrics["total_words"] > 5000:
            insights.append("📄 Moderate content volume generated")
        
        # Performance insights
        perf_metrics = analytics["performance_metrics"]
        if perf_metrics["total_execution_time"] > 300:  # 5 minutes
            insights.append("⏱️ Long execution time - consider optimization")
        elif perf_metrics["total_execution_time"] < 30:  # 30 seconds
            insights.append("⚡ Fast execution time - efficient workflow")
        
        # Quality insights
        quality_metrics = analytics["quality_metrics"]
        if quality_metrics["avg_validation_score"] and quality_metrics["avg_validation_score"] > 0.9:
            insights.append("🏆 High quality outputs with excellent validation scores")
        elif quality_metrics["outputs_with_errors"] > 0:
            insights.append(f"⚠️ {quality_metrics['outputs_with_errors']} outputs have validation errors")
        
        # Agent insights
        agent_perf = analytics["agent_performance"]
        best_agent = max(agent_perf.items(), key=lambda x: x[1]["success_rate"], default=None)
        if best_agent and best_agent[1]["success_rate"] == 1.0:
            insights.append(f"🌟 {best_agent[0]} achieved perfect performance")
        
        # Diversity insights
        output_types = Counter(output.output_type for output in self.outputs)
        if len(output_types) > 1:
            insights.append(f"🎨 Diverse output types: {', '.join(output_types.keys())}")
        
        return insights


class ResultAggregator:
    """
    Aggregates and analyzes multiple agent outputs to create comprehensive
    workflow results with insights and analytics.
    """
    
    def __init__(self, formatter: Optional[OutputFormatter] = None):
        self.logger = logging.getLogger(__name__)
        self.formatter = formatter or OutputFormatter()
    
    def aggregate_workflow_results(
        self,
        outputs: List[StructuredOutput],
        workflow_id: str,
        workflow_name: str,
        execution_start: Optional[datetime] = None,
        execution_end: Optional[datetime] = None
    ) -> WorkflowResult:
        """
        Aggregate outputs from a complete workflow execution.
        
        Args:
            outputs: List of structured outputs from agents
            workflow_id: Unique identifier for the workflow
            workflow_name: Human-readable workflow name
            execution_start: When workflow execution started
            execution_end: When workflow execution ended
            
        Returns:
            WorkflowResult with aggregated data and insights
        """
        # Set default timestamps if not provided
        if execution_end is None:
            execution_end = datetime.now()
        if execution_start is None:
            # Estimate start time from earliest output timestamp
            earliest_timestamp = min(
                (output.metadata.timestamp for output in outputs),
                default=execution_end - timedelta(seconds=sum(
                    output.metadata.execution_time or 0 for output in outputs
                ))
            )
            execution_start = earliest_timestamp
        
        return WorkflowResult(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            outputs=outputs,
            execution_start=execution_start,
            execution_end=execution_end
        )
    
    def create_consolidated_output(
        self,
        outputs: List[StructuredOutput],
        consolidation_strategy: str = "merge",
        target_agent_role: str = "Consolidated Agent"
    ) -> StructuredOutput:
        """
        Create a single consolidated output from multiple outputs.
        
        Args:
            outputs: List of outputs to consolidate
            consolidation_strategy: Strategy for consolidation ('merge', 'summary', 'best')
            target_agent_role: Role for the consolidated agent
            
        Returns:
            Single consolidated structured output
        """
        if not outputs:
            raise ValueError("No outputs provided for consolidation")
        
        if consolidation_strategy == "merge":
            return self._merge_outputs(outputs, target_agent_role)
        elif consolidation_strategy == "summary":
            return self._summarize_outputs(outputs, target_agent_role)
        elif consolidation_strategy == "best":
            return self._select_best_output(outputs, target_agent_role)
        else:
            raise ValueError(f"Unknown consolidation strategy: {consolidation_strategy}")
    
    def _merge_outputs(self, outputs: List[StructuredOutput], agent_role: str) -> StructuredOutput:
        """Merge multiple outputs into a single comprehensive output."""
        
        # Combine all content
        merged_content_parts = []
        merged_sections = {}
        all_tags = set()
        all_keywords = set()
        
        for i, output in enumerate(outputs):
            # Add content with agent attribution
            agent_name = output.metadata.agent_role
            merged_content_parts.append(f"## {agent_name} Output\n\n{str(output.content)}")
            
            # Merge sections
            if output.sections:
                for section_name, section_content in output.sections.items():
                    prefixed_section = f"{agent_name.lower().replace(' ', '_')}_{section_name}"
                    merged_sections[prefixed_section] = section_content
            
            # Collect tags and keywords
            all_tags.update(output.tags)
            all_keywords.update(output.keywords)
        
        # Calculate aggregate metadata
        total_words = sum(output.metadata.word_count or 0 for output in outputs)
        total_execution_time = sum(output.metadata.execution_time or 0 for output in outputs)
        avg_confidence = mean([output.metadata.confidence_score for output in outputs if output.metadata.confidence_score]) if any(output.metadata.confidence_score for output in outputs) else None
        
        # Determine overall status
        status_priority = {OutputStatus.FAILED: 0, OutputStatus.PARTIAL: 1, OutputStatus.SUCCESS: 2}
        overall_status = min(outputs, key=lambda x: status_priority.get(x.status, 0)).status
        
        consolidated_output = StructuredOutput(
            content="\n\n".join(merged_content_parts),
            output_type=OutputType.MARKDOWN,
            status=overall_status,
            metadata=OutputMetadata(
                agent_id="consolidated",
                agent_role=agent_role,
                workflow_id=outputs[0].metadata.workflow_id if outputs else None,
                word_count=total_words,
                execution_time=total_execution_time,
                confidence_score=avg_confidence,
                source_count=sum(output.metadata.source_count or 0 for output in outputs)
            ),
            sections=merged_sections,
            tags=list(all_tags),
            keywords=list(all_keywords),
            processing_notes=[f"Consolidated from {len(outputs)} agent outputs"]
        )
        
        return consolidated_output
    
    def _summarize_outputs(self, outputs: List[StructuredOutput], agent_role: str) -> StructuredOutput:
        """Create a summary of multiple outputs."""
        
        summary_parts = []
        summary_parts.append("# Workflow Summary\n")
        
        # Overview
        summary_parts.append(f"This summary consolidates results from {len(outputs)} agents:\n")
        for output in outputs:
            status_emoji = "✅" if output.status == OutputStatus.SUCCESS else "⚠️" if output.status == OutputStatus.PARTIAL else "❌"
            summary_parts.append(f"- {status_emoji} **{output.metadata.agent_role}**: {output.get_content_preview(100)}")
        
        summary_parts.append("\n## Key Findings\n")
        
        # Extract key sections from each output
        key_sections = defaultdict(list)
        for output in outputs:
            if output.sections:
                for section_name, section_content in output.sections.items():
                    if section_name.lower() in ['summary', 'findings', 'conclusion', 'recommendations']:
                        key_sections[section_name].append(f"**{output.metadata.agent_role}**: {str(section_content)[:300]}...")
        
        for section_name, content_list in key_sections.items():
            summary_parts.append(f"### {section_name.title()}\n")
            summary_parts.extend(content_list)
            summary_parts.append("")
        
        # Aggregate metrics
        total_words = sum(output.metadata.word_count or 0 for output in outputs)
        avg_confidence = mean([output.metadata.confidence_score for output in outputs if output.metadata.confidence_score]) if any(output.metadata.confidence_score for output in outputs) else None
        
        summary_parts.append("## Workflow Metrics\n")
        summary_parts.append(f"- **Total Word Count**: {total_words:,}")
        summary_parts.append(f"- **Average Confidence**: {avg_confidence:.1%}" if avg_confidence else "- **Average Confidence**: N/A")
        summary_parts.append(f"- **Successful Outputs**: {sum(1 for o in outputs if o.status == OutputStatus.SUCCESS)}/{len(outputs)}")
        
        summary_output = StructuredOutput(
            content="\n".join(summary_parts),
            output_type=OutputType.MARKDOWN,
            status=OutputStatus.SUCCESS,
            metadata=OutputMetadata(
                agent_id="summary",
                agent_role=agent_role,
                workflow_id=outputs[0].metadata.workflow_id if outputs else None,
                word_count=len("\n".join(summary_parts).split()),
                source_count=sum(output.metadata.source_count or 0 for output in outputs)
            ),
            processing_notes=[f"Summary generated from {len(outputs)} agent outputs"]
        )
        
        return summary_output
    
    def _select_best_output(self, outputs: List[StructuredOutput], agent_role: str) -> StructuredOutput:
        """Select the best output based on quality metrics."""
        
        def score_output(output: StructuredOutput) -> float:
            score = 0.0
            
            # Status score
            if output.status == OutputStatus.SUCCESS:
                score += 3.0
            elif output.status == OutputStatus.PARTIAL:
                score += 1.0
            
            # Validation score
            if output.validation:
                score += output.validation.validation_score * 2.0
            
            # Content quality indicators
            if output.metadata.word_count:
                # Prefer outputs with substantial content but not excessively long
                word_score = min(output.metadata.word_count / 1000, 2.0)
                score += word_score
            
            # Confidence score
            if output.metadata.confidence_score:
                score += output.metadata.confidence_score * 1.0
            
            # Completeness (has sections)
            if output.sections:
                score += len(output.sections) * 0.1
            
            return score
        
        # Find the best output
        best_output = max(outputs, key=score_output)
        
        # Clone the best output with updated metadata
        best_copy = StructuredOutput(
            content=best_output.content,
            output_type=best_output.output_type,
            status=best_output.status,
            metadata=OutputMetadata(
                agent_id="best_selected",
                agent_role=agent_role,
                task_id=best_output.metadata.task_id,
                task_name=best_output.metadata.task_name,
                workflow_id=best_output.metadata.workflow_id,
                word_count=best_output.metadata.word_count,
                execution_time=best_output.metadata.execution_time,
                confidence_score=best_output.metadata.confidence_score,
                source_count=best_output.metadata.source_count
            ),
            validation=best_output.validation,
            sections=best_output.sections,
            tags=best_output.tags,
            keywords=best_output.keywords,
            processing_notes=best_output.processing_notes + [f"Selected as best from {len(outputs)} outputs"]
        )
        
        return best_copy
    
    def generate_comparison_report(
        self,
        outputs: List[StructuredOutput],
        comparison_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a detailed comparison report between multiple outputs.
        
        Args:
            outputs: List of outputs to compare
            comparison_criteria: Specific criteria to compare (default: all)
            
        Returns:
            Detailed comparison report
        """
        if len(outputs) < 2:
            return {"error": "Need at least 2 outputs for comparison"}
        
        criteria = comparison_criteria or [
            "word_count", "execution_time", "confidence_score", 
            "validation_score", "status", "content_type"
        ]
        
        comparison = {
            "output_count": len(outputs),
            "comparison_criteria": criteria,
            "agents": [output.metadata.agent_role for output in outputs],
            "detailed_comparison": {}
        }
        
        for criterion in criteria:
            comparison["detailed_comparison"][criterion] = self._compare_by_criterion(outputs, criterion)
        
        # Overall ranking
        comparison["ranking"] = self._rank_outputs(outputs)
        
        return comparison
    
    def _compare_by_criterion(self, outputs: List[StructuredOutput], criterion: str) -> Dict[str, Any]:
        """Compare outputs by a specific criterion."""
        values = []
        
        for output in outputs:
            if criterion == "word_count":
                values.append(output.metadata.word_count or 0)
            elif criterion == "execution_time":
                values.append(output.metadata.execution_time or 0)
            elif criterion == "confidence_score":
                values.append(output.metadata.confidence_score or 0)
            elif criterion == "validation_score":
                values.append(output.validation.validation_score if output.validation else 0)
            elif criterion == "status":
                values.append(output.status)
            elif criterion == "content_type":
                values.append(output.output_type)
            else:
                values.append("N/A")
        
        result = {
            "values": values,
            "agents": [output.metadata.agent_role for output in outputs]
        }
        
        # Add statistics for numeric values
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        if numeric_values:
            result.update({
                "min": min(numeric_values),
                "max": max(numeric_values),
                "avg": mean(numeric_values),
                "median": median(numeric_values)
            })
        
        return result
    
    def _rank_outputs(self, outputs: List[StructuredOutput]) -> List[Dict[str, Any]]:
        """Rank outputs by overall quality score."""
        scored_outputs = []
        
        for i, output in enumerate(outputs):
            score = 0.0
            
            # Status weight
            if output.status == OutputStatus.SUCCESS:
                score += 30
            elif output.status == OutputStatus.PARTIAL:
                score += 15
            
            # Validation weight
            if output.validation:
                score += output.validation.validation_score * 25
            
            # Content weight
            if output.metadata.word_count:
                score += min(output.metadata.word_count / 100, 20)
            
            # Confidence weight
            if output.metadata.confidence_score:
                score += output.metadata.confidence_score * 15
            
            # Completeness weight
            if output.sections:
                score += min(len(output.sections) * 2, 10)
            
            scored_outputs.append({
                "rank": 0,  # Will be set after sorting
                "agent": output.metadata.agent_role,
                "score": round(score, 2),
                "status": output.status,
                "word_count": output.metadata.word_count,
                "validation_score": output.validation.validation_score if output.validation else None
            })
        
        # Sort by score and assign ranks
        scored_outputs.sort(key=lambda x: x["score"], reverse=True)
        for i, item in enumerate(scored_outputs):
            item["rank"] = i + 1
        
        return scored_outputs 