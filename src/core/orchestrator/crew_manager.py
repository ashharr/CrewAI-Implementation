"""
CrewManager - Core orchestration engine for managing multi-agent workflows.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from crewai import Crew
from pydantic import BaseModel, Field

from ..monitoring.workflow_monitor import WorkflowMonitor


class WorkflowConfig(BaseModel):
    """Configuration for a workflow execution."""
    name: str = Field(..., description="Workflow name")
    description: str = Field("", description="Workflow description")
    agents: List[Dict[str, Any]] = Field([], description="Agent configurations")
    tasks: List[Dict[str, Any]] = Field([], description="Task configurations") 
    inputs: Dict[str, Any] = Field({}, description="Input parameters")
    output_dir: Optional[str] = Field(None, description="Output directory")


class CrewManager:
    """
    Central orchestration engine for managing CrewAI workflows.
    
    Handles workflow loading, execution, monitoring, and result management.
    """
    
    def __init__(self, monitor: Optional[WorkflowMonitor] = None):
        self.logger = logging.getLogger(__name__)
        self.monitor = monitor or WorkflowMonitor()
        self.active_crews: Dict[str, Crew] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def load_workflow(self, config: WorkflowConfig) -> str:
        """
        Load a workflow configuration and prepare it for execution.
        
        Args:
            config: Workflow configuration
            
        Returns:
            Workflow ID for tracking
        """
        workflow_id = f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Create agents and tasks from configuration
            agents = self._create_agents(config.agents)
            tasks = self._create_tasks(config.tasks, agents)
            
            # Initialize crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=True
            )
            
            self.active_crews[workflow_id] = crew
            
            self.logger.info(f"Workflow {workflow_id} loaded successfully")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to load workflow {config.name}: {e}")
            raise
    
    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a loaded workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            inputs: Runtime inputs for the workflow
            
        Returns:
            Execution results
        """
        if workflow_id not in self.active_crews:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        crew = self.active_crews[workflow_id]
        execution_inputs = inputs or {}
        
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting execution of workflow {workflow_id}")
            self.monitor.start_execution(workflow_id)
            
            # Execute the crew
            result = crew.kickoff(inputs=execution_inputs)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Record execution
            execution_record = {
                'workflow_id': workflow_id,
                'start_time': start_time,
                'end_time': end_time,
                'execution_time': execution_time,
                'status': 'success',
                'result': str(result),
                'inputs': execution_inputs
            }
            
            self.execution_history.append(execution_record)
            self.monitor.end_execution(workflow_id, True, execution_time)
            
            self.logger.info(f"Workflow {workflow_id} completed successfully in {execution_time:.2f}s")
            
            return {
                'workflow_id': workflow_id,
                'status': 'success',
                'result': result,
                'execution_time': execution_time,
                'timestamp': end_time
            }
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            execution_record = {
                'workflow_id': workflow_id,
                'start_time': start_time,
                'end_time': end_time,
                'execution_time': execution_time,
                'status': 'failed',
                'error': str(e),
                'inputs': execution_inputs
            }
            
            self.execution_history.append(execution_record)
            self.monitor.end_execution(workflow_id, False, execution_time)
            
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            raise
    
    def get_execution_history(self, workflow_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get execution history, optionally filtered by workflow name."""
        if workflow_name:
            return [
                record for record in self.execution_history 
                if record['workflow_id'].startswith(workflow_name)
            ]
        return self.execution_history.copy()
    
    def cleanup_workflow(self, workflow_id: str) -> bool:
        """Remove a workflow from active crews."""
        if workflow_id in self.active_crews:
            del self.active_crews[workflow_id]
            self.logger.info(f"Workflow {workflow_id} cleaned up")
            return True
        return False
    
    def _create_agents(self, agent_configs: List[Dict[str, Any]]) -> List:
        """Create agents from configuration."""
        # This would be implemented based on your agent configuration format
        # For now, return empty list as placeholder
        return []
    
    def _create_tasks(self, task_configs: List[Dict[str, Any]], agents: List) -> List:
        """Create tasks from configuration."""
        # This would be implemented based on your task configuration format
        # For now, return empty list as placeholder
        return [] 