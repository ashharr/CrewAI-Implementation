"""
Tests for WorkflowMonitor functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from collections import deque

from src.core.monitoring.workflow_monitor import WorkflowMonitor


class TestWorkflowMonitor:
    """Test suite for WorkflowMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a WorkflowMonitor instance without Prometheus."""
        return WorkflowMonitor(enable_prometheus=False, prometheus_port=None)
    
    @pytest.fixture
    def monitor_with_prometheus(self):
        """Create a WorkflowMonitor instance with mocked Prometheus."""
        with patch('src.core.monitoring.workflow_monitor.PROMETHEUS_AVAILABLE', True):
            with patch('src.core.monitoring.workflow_monitor.start_http_server'):
                with patch('src.core.monitoring.workflow_monitor.Counter'):
                    with patch('src.core.monitoring.workflow_monitor.Histogram'):
                        with patch('src.core.monitoring.workflow_monitor.Gauge'):
                            return WorkflowMonitor(enable_prometheus=True, prometheus_port=8000)
    
    def test_monitor_initialization_without_prometheus(self, monitor):
        """Test WorkflowMonitor initialization without Prometheus."""
        assert monitor.enable_prometheus is False
        assert isinstance(monitor.execution_metrics, dict)
        assert isinstance(monitor.active_executions, dict)
        assert isinstance(monitor.performance_history, deque)
        assert monitor.execution_time_threshold == 300
        assert monitor.error_rate_threshold == 0.1
    
    def test_monitor_initialization_with_prometheus(self, monitor_with_prometheus):
        """Test WorkflowMonitor initialization with Prometheus."""
        assert monitor_with_prometheus.enable_prometheus is True
    
    def test_start_execution(self, monitor):
        """Test starting execution monitoring."""
        workflow_id = "test_workflow_20240101_100000"
        metadata = {"user": "test_user", "priority": "high"}
        
        with patch('src.core.monitoring.workflow_monitor.datetime') as mock_datetime:
            start_time = datetime(2024, 1, 1, 10, 0, 0)
            mock_datetime.now.return_value = start_time
            
            monitor.start_execution(workflow_id, metadata)
        
        # Verify execution was recorded
        assert workflow_id in monitor.active_executions
        execution_data = monitor.active_executions[workflow_id]
        
        assert execution_data['workflow_id'] == workflow_id
        assert execution_data['workflow_name'] == 'test'
        assert execution_data['start_time'] == start_time
        assert execution_data['metadata'] == metadata
    
    def test_start_execution_without_metadata(self, monitor):
        """Test starting execution monitoring without metadata."""
        workflow_id = "simple_workflow_20240101_100000"
        
        monitor.start_execution(workflow_id)
        
        assert workflow_id in monitor.active_executions
        execution_data = monitor.active_executions[workflow_id]
        assert execution_data['metadata'] == {}
    
    def test_end_execution_success(self, monitor):
        """Test ending execution monitoring for successful execution."""
        workflow_id = "test_workflow_20240101_100000"
        
        # Start execution first
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        monitor.active_executions[workflow_id] = {
            'workflow_id': workflow_id,
            'workflow_name': 'test',
            'start_time': start_time,
            'metadata': {}
        }
        
        execution_time = 120.5
        result_data = {"output": "success"}
        
        with patch('src.core.monitoring.workflow_monitor.datetime') as mock_datetime:
            end_time = datetime(2024, 1, 1, 10, 2, 0)
            mock_datetime.now.return_value = end_time
            
            monitor.end_execution(workflow_id, True, execution_time, result_data)
        
        # Verify execution was removed from active
        assert workflow_id not in monitor.active_executions
        
        # Verify metrics were recorded
        assert 'test' in monitor.execution_metrics
        assert len(monitor.execution_metrics['test']) == 1
        
        execution_record = monitor.execution_metrics['test'][0]
        assert execution_record['workflow_id'] == workflow_id
        assert execution_record['success'] is True
        assert execution_record['execution_time'] == execution_time
        assert execution_record['result_data'] == result_data
        
        # Verify performance history
        assert len(monitor.performance_history) == 1
        assert monitor.performance_history[0] == execution_record
    
    def test_end_execution_failure(self, monitor):
        """Test ending execution monitoring for failed execution."""
        workflow_id = "failed_workflow_20240101_100000"
        
        # Start execution first
        monitor.active_executions[workflow_id] = {
            'workflow_id': workflow_id,
            'workflow_name': 'failed',
            'start_time': datetime(2024, 1, 1, 10, 0, 0),
            'metadata': {}
        }
        
        execution_time = 60.0
        
        monitor.end_execution(workflow_id, False, execution_time)
        
        # Verify execution was recorded as failed
        assert 'failed' in monitor.execution_metrics
        execution_record = monitor.execution_metrics['failed'][0]
        assert execution_record['success'] is False
        assert execution_record['execution_time'] == execution_time
    
    def test_end_execution_not_found(self, monitor):
        """Test ending execution for non-existent workflow."""
        # Should not raise exception, just log warning
        monitor.end_execution("nonexistent", True, 100.0)
        
        # Verify no metrics were recorded
        assert len(monitor.execution_metrics) == 0
    
    def test_get_workflow_metrics_success(self, monitor):
        """Test getting workflow metrics for existing workflow."""
        workflow_name = "test_workflow"
        
        # Add some mock execution data
        executions = [
            {
                'workflow_name': workflow_name,
                'start_time': datetime.now() - timedelta(hours=1),
                'execution_time': 120.0,
                'success': True
            },
            {
                'workflow_name': workflow_name,
                'start_time': datetime.now() - timedelta(minutes=30),
                'execution_time': 90.0,
                'success': True
            },
            {
                'workflow_name': workflow_name,
                'start_time': datetime.now() - timedelta(minutes=15),
                'execution_time': 150.0,
                'success': False
            }
        ]
        monitor.execution_metrics[workflow_name] = executions
        
        metrics = monitor.get_workflow_metrics(workflow_name)
        
        assert metrics['workflow_name'] == workflow_name
        assert metrics['total_executions'] == 3
        assert metrics['successful_executions'] == 2
        assert metrics['failed_executions'] == 1
        assert metrics['success_rate'] == 2/3
        assert metrics['avg_execution_time'] == 120.0  # (120 + 90 + 150) / 3
        assert metrics['min_execution_time'] == 90.0
        assert metrics['max_execution_time'] == 150.0
    
    def test_get_workflow_metrics_not_found(self, monitor):
        """Test getting metrics for non-existent workflow."""
        metrics = monitor.get_workflow_metrics("nonexistent")
        
        assert 'error' in metrics
        assert 'No metrics found' in metrics['error']
    
    def test_get_workflow_metrics_with_time_window(self, monitor):
        """Test getting workflow metrics with time window filter."""
        workflow_name = "test_workflow"
        now = datetime.now()
        
        # Add executions with different timestamps
        executions = [
            {
                'workflow_name': workflow_name,
                'start_time': now - timedelta(hours=2),  # Outside window
                'execution_time': 120.0,
                'success': True
            },
            {
                'workflow_name': workflow_name,
                'start_time': now - timedelta(minutes=30),  # Inside window
                'execution_time': 90.0,
                'success': True
            }
        ]
        monitor.execution_metrics[workflow_name] = executions
        
        # Get metrics for last hour
        time_window = timedelta(hours=1)
        metrics = monitor.get_workflow_metrics(workflow_name, time_window)
        
        assert metrics['total_executions'] == 1
        assert metrics['avg_execution_time'] == 90.0
    
    def test_get_system_health_empty(self, monitor):
        """Test getting system health with no executions."""
        health = monitor.get_system_health()
        
        assert health['active_workflows'] == 0
        assert health['total_registered_workflows'] == 0
        assert health['overall_success_rate'] == 1.0
        assert health['avg_execution_time'] == 0.0
        assert health['prometheus_enabled'] is False
        assert 'timestamp' in health
    
    def test_get_system_health_with_data(self, monitor):
        """Test getting system health with execution data."""
        # Add some active executions
        monitor.active_executions['active1'] = {}
        monitor.active_executions['active2'] = {}
        
        # Add some execution metrics
        monitor.execution_metrics['workflow1'] = [
            {'execution_time': 100.0, 'success': True},
            {'execution_time': 200.0, 'success': False}
        ]
        monitor.execution_metrics['workflow2'] = [
            {'execution_time': 150.0, 'success': True}
        ]
        
        health = monitor.get_system_health()
        
        assert health['active_workflows'] == 2
        assert health['total_registered_workflows'] == 2
        assert health['overall_success_rate'] == 2/3  # 2 success out of 3 total
        assert health['avg_execution_time'] == 150.0  # (100 + 200 + 150) / 3
    
    def test_check_performance_alerts_slow_execution(self, monitor):
        """Test performance alerts for slow execution."""
        workflow_name = "slow_workflow"
        execution_time = 400.0  # Above threshold of 300
        
        alerts = monitor._check_performance_alerts(workflow_name, execution_time, True)
        
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert['type'] == 'slow_execution'
        assert alert['workflow_name'] == workflow_name
        assert alert['execution_time'] == execution_time
        assert alert['threshold'] == 300
    
    def test_check_performance_alerts_high_error_rate(self, monitor):
        """Test performance alerts for high error rate."""
        workflow_name = "error_prone_workflow"
        
        # Add execution history with high error rate
        executions = [
            {'success': False},  # Error
            {'success': False},  # Error
            {'success': False},  # Error
            {'success': True},   # Success
            {'success': False}   # Error
        ]
        monitor.execution_metrics[workflow_name] = executions
        
        alerts = monitor._check_performance_alerts(workflow_name, 100.0, False)
        
        # Should trigger high error rate alert (4/5 = 80% > 10% threshold)
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert['type'] == 'high_error_rate'
        assert alert['workflow_name'] == workflow_name
        assert alert['error_rate'] == 0.8
    
    def test_check_performance_alerts_insufficient_data(self, monitor):
        """Test performance alerts with insufficient data."""
        workflow_name = "new_workflow"
        
        # Add only 3 executions (less than 5 required)
        executions = [
            {'success': False},
            {'success': False},
            {'success': False}
        ]
        monitor.execution_metrics[workflow_name] = executions
        
        alerts = monitor._check_performance_alerts(workflow_name, 100.0, False)
        
        # Should not trigger error rate alert due to insufficient data
        assert len(alerts) == 0
    
    def test_track_execution_legacy(self, monitor):
        """Test legacy track_execution method."""
        # Should not raise exception
        monitor.track_execution("some_result")
    
    def test_log_performance_metrics_legacy(self, monitor):
        """Test legacy log_performance_metrics method."""
        # Should not raise exception
        monitor.log_performance_metrics()
    
    @patch('src.core.monitoring.workflow_monitor.PROMETHEUS_AVAILABLE', True)
    def test_prometheus_metrics_update(self):
        """Test Prometheus metrics updates."""
        with patch('src.core.monitoring.workflow_monitor.start_http_server'):
            with patch('src.core.monitoring.workflow_monitor.Counter') as mock_counter:
                with patch('src.core.monitoring.workflow_monitor.Histogram') as mock_histogram:
                    with patch('src.core.monitoring.workflow_monitor.Gauge') as mock_gauge:
                        
                        # Create monitor with Prometheus enabled
                        monitor = WorkflowMonitor(enable_prometheus=True, prometheus_port=8000)
                        
                        # Mock the metric instances
                        mock_counter_instance = Mock()
                        mock_histogram_instance = Mock()
                        mock_gauge_instance = Mock()
                        
                        monitor.workflow_executions_total = mock_counter_instance
                        monitor.workflow_execution_duration = mock_histogram_instance
                        monitor.active_workflows = mock_gauge_instance
                        
                        # Start and end execution
                        workflow_id = "test_workflow_123"
                        monitor.start_execution(workflow_id)
                        monitor.end_execution(workflow_id, True, 120.0)
                        
                        # Verify Prometheus metrics were called
                        mock_gauge_instance.inc.assert_called_once()
                        mock_gauge_instance.dec.assert_called_once()
                        mock_counter_instance.labels.assert_called()
                        mock_histogram_instance.labels.assert_called() 