"""
Tests for CrewManager orchestration functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.core.orchestrator.crew_manager import CrewManager, WorkflowConfig
from src.core.monitoring.workflow_monitor import WorkflowMonitor


class TestCrewManager:
    """Test suite for CrewManager class."""
    
    @pytest.fixture
    def mock_monitor(self):
        """Create a mock WorkflowMonitor."""
        return Mock(spec=WorkflowMonitor)
    
    @pytest.fixture
    def crew_manager(self, mock_monitor):
        """Create a CrewManager instance with mocked monitor."""
        return CrewManager(monitor=mock_monitor)
    
    @pytest.fixture
    def sample_workflow_config(self):
        """Create a sample workflow configuration."""
        return WorkflowConfig(
            name="test_workflow",
            description="A test workflow",
            agents=[
                {"role": "researcher", "goal": "research topics"},
                {"role": "writer", "goal": "write content"}
            ],
            tasks=[
                {"description": "research the topic", "agent": "researcher"},
                {"description": "write a blog post", "agent": "writer"}
            ],
            inputs={"topic": "AI development"}
        )
    
    def test_crew_manager_initialization(self, mock_monitor):
        """Test CrewManager initialization."""
        manager = CrewManager(monitor=mock_monitor)
        
        assert manager.monitor == mock_monitor
        assert manager.active_crews == {}
        assert manager.execution_history == []
    
    def test_crew_manager_default_monitor(self):
        """Test CrewManager with default monitor."""
        manager = CrewManager()
        
        assert isinstance(manager.monitor, WorkflowMonitor)
        assert manager.active_crews == {}
        assert manager.execution_history == []
    
    @patch('src.core.orchestrator.crew_manager.Crew')
    def test_load_workflow_success(self, mock_crew_class, crew_manager, sample_workflow_config):
        """Test successful workflow loading."""
        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance
        
        # Mock the agent and task creation methods
        crew_manager._create_agents = Mock(return_value=[Mock(), Mock()])
        crew_manager._create_tasks = Mock(return_value=[Mock(), Mock()])
        
        workflow_id = crew_manager.load_workflow(sample_workflow_config)
        
        # Verify workflow ID format
        assert workflow_id.startswith("test_workflow_")
        assert len(workflow_id.split('_')) == 3  # name_date_time
        
        # Verify crew was created and stored
        assert workflow_id in crew_manager.active_crews
        assert crew_manager.active_crews[workflow_id] == mock_crew_instance
        
        # Verify Crew was initialized correctly
        mock_crew_class.assert_called_once_with(
            agents=[Mock(), Mock()],
            tasks=[Mock(), Mock()],
            verbose=True
        )
    
    def test_load_workflow_failure(self, crew_manager, sample_workflow_config):
        """Test workflow loading failure."""
        # Mock agent creation to raise an exception
        crew_manager._create_agents = Mock(side_effect=Exception("Agent creation failed"))
        
        with pytest.raises(Exception, match="Agent creation failed"):
            crew_manager.load_workflow(sample_workflow_config)
        
        # Verify no workflow was stored
        assert len(crew_manager.active_crews) == 0
    
    def test_execute_workflow_not_found(self, crew_manager):
        """Test executing a non-existent workflow."""
        with pytest.raises(ValueError, match="Workflow nonexistent not found"):
            crew_manager.execute_workflow("nonexistent")
    
    @patch('src.core.orchestrator.crew_manager.datetime')
    def test_execute_workflow_success(self, mock_datetime, crew_manager, mock_monitor):
        """Test successful workflow execution."""
        # Setup mock datetime
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        end_time = datetime(2024, 1, 1, 10, 5, 0)
        mock_datetime.now.side_effect = [start_time, end_time, end_time]
        
        # Setup mock crew
        mock_crew = Mock()
        mock_crew.kickoff.return_value = "Workflow completed successfully"
        workflow_id = "test_workflow_20240101_100000"
        crew_manager.active_crews[workflow_id] = mock_crew
        
        # Execute workflow
        inputs = {"topic": "AI development"}
        result = crew_manager.execute_workflow(workflow_id, inputs)
        
        # Verify execution
        mock_crew.kickoff.assert_called_once_with(inputs=inputs)
        mock_monitor.start_execution.assert_called_once_with(workflow_id)
        mock_monitor.end_execution.assert_called_once_with(workflow_id, True, 300.0)
        
        # Verify result
        assert result['workflow_id'] == workflow_id
        assert result['status'] == 'success'
        assert result['result'] == "Workflow completed successfully"
        assert result['execution_time'] == 300.0
        assert result['timestamp'] == end_time
        
        # Verify execution history
        assert len(crew_manager.execution_history) == 1
        history_record = crew_manager.execution_history[0]
        assert history_record['workflow_id'] == workflow_id
        assert history_record['status'] == 'success'
        assert history_record['execution_time'] == 300.0
    
    @patch('src.core.orchestrator.crew_manager.datetime')
    def test_execute_workflow_failure(self, mock_datetime, crew_manager, mock_monitor):
        """Test workflow execution failure."""
        # Setup mock datetime
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        end_time = datetime(2024, 1, 1, 10, 2, 30)
        mock_datetime.now.side_effect = [start_time, end_time]
        
        # Setup mock crew that fails
        mock_crew = Mock()
        mock_crew.kickoff.side_effect = Exception("Execution failed")
        workflow_id = "test_workflow_20240101_100000"
        crew_manager.active_crews[workflow_id] = mock_crew
        
        # Execute workflow and expect failure
        with pytest.raises(Exception, match="Execution failed"):
            crew_manager.execute_workflow(workflow_id)
        
        # Verify monitoring calls
        mock_monitor.start_execution.assert_called_once_with(workflow_id)
        mock_monitor.end_execution.assert_called_once_with(workflow_id, False, 150.0)
        
        # Verify execution history records failure
        assert len(crew_manager.execution_history) == 1
        history_record = crew_manager.execution_history[0]
        assert history_record['workflow_id'] == workflow_id
        assert history_record['status'] == 'failed'
        assert history_record['error'] == "Execution failed"
    
    def test_get_execution_history_all(self, crew_manager):
        """Test getting all execution history."""
        # Add some mock history
        crew_manager.execution_history = [
            {'workflow_id': 'workflow1_123', 'status': 'success'},
            {'workflow_id': 'workflow2_456', 'status': 'failed'},
            {'workflow_id': 'workflow1_789', 'status': 'success'}
        ]
        
        history = crew_manager.get_execution_history()
        
        assert len(history) == 3
        assert history == crew_manager.execution_history
        # Verify it returns a copy, not the original
        assert history is not crew_manager.execution_history
    
    def test_get_execution_history_filtered(self, crew_manager):
        """Test getting filtered execution history."""
        # Add some mock history
        crew_manager.execution_history = [
            {'workflow_id': 'workflow1_123', 'status': 'success'},
            {'workflow_id': 'workflow2_456', 'status': 'failed'},
            {'workflow_id': 'workflow1_789', 'status': 'success'}
        ]
        
        history = crew_manager.get_execution_history('workflow1')
        
        assert len(history) == 2
        assert all(record['workflow_id'].startswith('workflow1') for record in history)
    
    def test_cleanup_workflow_exists(self, crew_manager):
        """Test cleaning up an existing workflow."""
        workflow_id = "test_workflow_123"
        crew_manager.active_crews[workflow_id] = Mock()
        
        result = crew_manager.cleanup_workflow(workflow_id)
        
        assert result is True
        assert workflow_id not in crew_manager.active_crews
    
    def test_cleanup_workflow_not_exists(self, crew_manager):
        """Test cleaning up a non-existent workflow."""
        result = crew_manager.cleanup_workflow("nonexistent")
        
        assert result is False
    
    def test_create_agents_placeholder(self, crew_manager):
        """Test the placeholder _create_agents method."""
        agents = crew_manager._create_agents([{"role": "test"}])
        assert agents == []
    
    def test_create_tasks_placeholder(self, crew_manager):
        """Test the placeholder _create_tasks method."""
        tasks = crew_manager._create_tasks([{"description": "test"}], [])
        assert tasks == []


class TestWorkflowConfig:
    """Test suite for WorkflowConfig model."""
    
    def test_workflow_config_creation(self):
        """Test creating a WorkflowConfig instance."""
        config = WorkflowConfig(
            name="test_workflow",
            description="A test workflow",
            agents=[{"role": "researcher"}],
            tasks=[{"description": "research"}],
            inputs={"topic": "AI"},
            output_dir="/tmp/output"
        )
        
        assert config.name == "test_workflow"
        assert config.description == "A test workflow"
        assert config.agents == [{"role": "researcher"}]
        assert config.tasks == [{"description": "research"}]
        assert config.inputs == {"topic": "AI"}
        assert config.output_dir == "/tmp/output"
    
    def test_workflow_config_defaults(self):
        """Test WorkflowConfig with default values."""
        config = WorkflowConfig(name="minimal_workflow")
        
        assert config.name == "minimal_workflow"
        assert config.description == ""
        assert config.agents == []
        assert config.tasks == []
        assert config.inputs == {}
        assert config.output_dir is None
    
    def test_workflow_config_validation(self):
        """Test WorkflowConfig validation."""
        # Test missing required field
        with pytest.raises(ValueError):
            WorkflowConfig()  # Missing required 'name' field 