"""
CrewAI Platform - A comprehensive, extensible ecosystem for AI agent workflows.

This package provides:
- Multi-agent orchestration
- Tool ecosystem and integrations  
- Workflow management
- Monitoring and analytics
- Community contribution framework
"""

__version__ = "0.1.0"
__author__ = "CrewAI Platform Contributors"
__email__ = "contributors@crewai-platform.com"

from src.core.orchestrator.crew_manager import CrewManager
from src.core.monitoring.workflow_monitor import WorkflowMonitor

__all__ = [
    "CrewManager",
    "WorkflowMonitor",
] 