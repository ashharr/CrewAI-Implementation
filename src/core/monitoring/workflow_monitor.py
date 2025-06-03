"""
WorkflowMonitor - Performance monitoring and analytics for CrewAI workflows.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class WorkflowMonitor:
    """
    Monitoring and analytics system for CrewAI workflows.
    
    Tracks execution metrics, performance data, and provides alerting capabilities.
    """
    
    def __init__(self, enable_prometheus: bool = True, prometheus_port: int = 8000):
        self.logger = logging.getLogger(__name__)
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        
        # In-memory metrics storage
        self.execution_metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.performance_history: deque = deque(maxlen=1000)
        
        # Performance thresholds
        self.execution_time_threshold = 300  # 5 minutes
        self.error_rate_threshold = 0.1  # 10%
        
        # Initialize Prometheus metrics if available
        if self.enable_prometheus:
            self._init_prometheus_metrics()
            if prometheus_port:
                try:
                    start_http_server(prometheus_port)
                    self.logger.info(f"Prometheus metrics server started on port {prometheus_port}")
                except Exception as e:
                    self.logger.warning(f"Failed to start Prometheus server: {e}")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics collectors."""
        if not PROMETHEUS_AVAILABLE:
            return
            
        self.workflow_executions_total = Counter(
            'crewai_workflow_executions_total',
            'Total number of workflow executions',
            ['workflow_name', 'status']
        )
        
        self.workflow_execution_duration = Histogram(
            'crewai_workflow_execution_duration_seconds',
            'Workflow execution duration in seconds',
            ['workflow_name']
        )
        
        self.active_workflows = Gauge(
            'crewai_active_workflows',
            'Number of currently active workflows'
        )
        
        self.workflow_errors_total = Counter(
            'crewai_workflow_errors_total',
            'Total number of workflow errors',
            ['workflow_name', 'error_type']
        )
    
    def start_execution(self, workflow_id: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Start monitoring a workflow execution.
        
        Args:
            workflow_id: Unique identifier for the workflow
            metadata: Additional metadata about the execution
        """
        start_time = datetime.now()
        workflow_name = workflow_id.split('_')[0]  # Extract name from ID
        
        execution_data = {
            'workflow_id': workflow_id,
            'workflow_name': workflow_name,
            'start_time': start_time,
            'metadata': metadata or {}
        }
        
        self.active_executions[workflow_id] = execution_data
        
        if self.enable_prometheus:
            self.active_workflows.inc()
        
        self.logger.info(f"Started monitoring workflow: {workflow_id}")
    
    def end_execution(self, workflow_id: str, success: bool, execution_time: float, 
                     result_data: Optional[Dict[str, Any]] = None):
        """
        End monitoring for a workflow execution.
        
        Args:
            workflow_id: Workflow identifier
            success: Whether the execution was successful
            execution_time: Total execution time in seconds
            result_data: Additional result data
        """
        if workflow_id not in self.active_executions:
            self.logger.warning(f"Workflow {workflow_id} not found in active executions")
            return
        
        execution_data = self.active_executions.pop(workflow_id)
        workflow_name = execution_data['workflow_name']
        
        # Create execution record
        execution_record = {
            **execution_data,
            'end_time': datetime.now(),
            'execution_time': execution_time,
            'success': success,
            'result_data': result_data or {}
        }
        
        # Store metrics
        self.execution_metrics[workflow_name].append(execution_record)
        self.performance_history.append(execution_record)
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            status = 'success' if success else 'failure'
            self.workflow_executions_total.labels(
                workflow_name=workflow_name, status=status
            ).inc()
            
            self.workflow_execution_duration.labels(
                workflow_name=workflow_name
            ).observe(execution_time)
            
            self.active_workflows.dec()
            
            if not success:
                self.workflow_errors_total.labels(
                    workflow_name=workflow_name, error_type='execution_failed'
                ).inc()
        
        # Check for performance alerts
        self._check_performance_alerts(workflow_name, execution_time, success)
        
        status_msg = "successfully" if success else "with errors"
        self.logger.info(f"Workflow {workflow_id} completed {status_msg} in {execution_time:.2f}s")
    
    def get_workflow_metrics(self, workflow_name: str, 
                           time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get metrics for a specific workflow.
        
        Args:
            workflow_name: Name of the workflow
            time_window: Optional time window for metrics (defaults to last 24 hours)
            
        Returns:
            Dictionary containing workflow metrics
        """
        if workflow_name not in self.execution_metrics:
            return {'error': f'No metrics found for workflow: {workflow_name}'}
        
        executions = self.execution_metrics[workflow_name]
        
        # Filter by time window if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            executions = [
                exec_data for exec_data in executions
                if exec_data['start_time'] >= cutoff_time
            ]
        
        if not executions:
            return {'error': 'No executions found in specified time window'}
        
        # Calculate metrics
        total_executions = len(executions)
        successful_executions = sum(1 for exec_data in executions if exec_data['success'])
        failed_executions = total_executions - successful_executions
        
        execution_times = [exec_data['execution_time'] for exec_data in executions]
        avg_execution_time = sum(execution_times) / len(execution_times)
        min_execution_time = min(execution_times)
        max_execution_time = max(execution_times)
        
        success_rate = successful_executions / total_executions if total_executions > 0 else 0
        
        return {
            'workflow_name': workflow_name,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'min_execution_time': min_execution_time,
            'max_execution_time': max_execution_time,
            'time_window': str(time_window) if time_window else 'all_time'
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        active_workflows = len(self.active_executions)
        total_workflows = len(self.execution_metrics)
        
        # Calculate overall success rate
        all_executions = []
        for workflow_executions in self.execution_metrics.values():
            all_executions.extend(workflow_executions)
        
        if all_executions:
            successful = sum(1 for exec_data in all_executions if exec_data['success'])
            overall_success_rate = successful / len(all_executions)
            
            execution_times = [exec_data['execution_time'] for exec_data in all_executions]
            avg_execution_time = sum(execution_times) / len(execution_times)
        else:
            overall_success_rate = 1.0
            avg_execution_time = 0.0
        
        return {
            'active_workflows': active_workflows,
            'total_registered_workflows': total_workflows,
            'overall_success_rate': overall_success_rate,
            'avg_execution_time': avg_execution_time,
            'prometheus_enabled': self.enable_prometheus,
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_performance_alerts(self, workflow_name: str, execution_time: float, success: bool):
        """Check for performance issues and generate alerts."""
        alerts = []
        
        # Check execution time threshold
        if execution_time > self.execution_time_threshold:
            alert = {
                'type': 'slow_execution',
                'workflow_name': workflow_name,
                'execution_time': execution_time,
                'threshold': self.execution_time_threshold,
                'timestamp': datetime.now()
            }
            alerts.append(alert)
            self.logger.warning(f"Slow execution alert: {workflow_name} took {execution_time:.2f}s")
        
        # Check error rate
        if workflow_name in self.execution_metrics:
            recent_executions = self.execution_metrics[workflow_name][-10:]  # Last 10 executions
            if len(recent_executions) >= 5:  # Only check if we have enough data
                error_rate = sum(1 for exec_data in recent_executions if not exec_data['success']) / len(recent_executions)
                
                if error_rate > self.error_rate_threshold:
                    alert = {
                        'type': 'high_error_rate',
                        'workflow_name': workflow_name,
                        'error_rate': error_rate,
                        'threshold': self.error_rate_threshold,
                        'timestamp': datetime.now()
                    }
                    alerts.append(alert)
                    self.logger.warning(f"High error rate alert: {workflow_name} has {error_rate:.2%} error rate")
        
        return alerts
    
    def track_execution(self, workflow_result: Any):
        """
        Legacy method for backward compatibility.
        
        Args:
            workflow_result: Result from workflow execution
        """
        self.logger.info("Workflow execution tracked (legacy method)")
    
    def log_performance_metrics(self):
        """Legacy method for backward compatibility."""
        health = self.get_system_health()
        self.logger.info(f"System health: {health}") 