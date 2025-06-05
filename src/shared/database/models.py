"""
Database models for the AI Agent Platform.
Based on the Low-Level Design (LLD) specifications.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    ARRAY,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# User and Authentication Models
class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        name="user_id"
    )
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    roles = relationship("UserRole", back_populates="user")
    agents = relationship("Agent", back_populates="user")
    workflows = relationship("Workflow", back_populates="user")
    llm_models = relationship("LLMModel", back_populates="user")
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")
    workflow_executions = relationship("WorkflowExecution", back_populates="user")


class Role(Base):
    """Role model."""
    
    __tablename__ = "roles"
    
    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Relationships
    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    """User-Role association model."""
    
    __tablename__ = "user_roles"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.role_id"),
        primary_key=True
    )
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


# LLM Model Management
class LLMModel(Base):
    """LLM Model configuration model."""
    
    __tablename__ = "llm_models"
    
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True  # Can be null for global/admin-managed models
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)  # OpenAI, Anthropic, etc.
    model_identifier: Mapped[str] = mapped_column(String(255), nullable=False)  # gpt-4o, claude-3-opus, etc.
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(500))  # For Ollama or custom APIs
    config_params_json: Mapped[dict] = mapped_column(JSONB, default=dict)  # temperature, max_tokens, etc.
    
    # Relationships
    user = relationship("User", back_populates="llm_models")
    agents = relationship("Agent", back_populates="llm_model")


# Knowledge Base Models
class KnowledgeBase(Base):
    """Knowledge Base model."""
    
    __tablename__ = "knowledge_bases"
    
    kb_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # upload, web_url, direct_text
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )  # pending, indexing, ready, error
    vector_db_collection_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="knowledge_bases")
    documents = relationship("KBDocument", back_populates="knowledge_base")
    agent_associations = relationship("AgentKnowledgeBase", back_populates="knowledge_base")


class KBDocument(Base):
    """Knowledge Base Document model."""
    
    __tablename__ = "kb_documents"
    
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    kb_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_bases.kb_id"),
        nullable=False
    )
    original_file_name: Mapped[Optional[str]] = mapped_column(String(500))
    storage_path_or_url: Mapped[Optional[str]] = mapped_column(String(1000))
    content_hash: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending_processing"
    )  # pending_processing, processing, processed, error_processing
    num_chunks: Mapped[Optional[int]] = mapped_column(Integer)
    processed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")


# Agent Models
class Agent(Base):
    """Agent model."""
    
    __tablename__ = "agents"
    
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    backstory: Mapped[str] = mapped_column(Text, nullable=False)
    llm_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("llm_models.model_id"),
        nullable=False
    )
    tools_config: Mapped[list] = mapped_column(JSONB, default=list)  # Array of tool definitions
    verbose_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    memory_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    max_iter: Mapped[int] = mapped_column(Integer, default=15)
    max_rpm: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    llm_model = relationship("LLMModel", back_populates="agents")
    knowledge_base_associations = relationship("AgentKnowledgeBase", back_populates="agent")
    workflow_agents = relationship("WorkflowAgent", back_populates="agent")
    task_executions = relationship("TaskExecution", back_populates="assigned_agent")


class AgentKnowledgeBase(Base):
    """Agent-Knowledge Base association model."""
    
    __tablename__ = "agent_knowledge_bases"
    
    agent_kb_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.agent_id"),
        nullable=False
    )
    kb_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_bases.kb_id"),
        nullable=False
    )
    
    # Ensure unique agent-KB associations
    __table_args__ = (UniqueConstraint("agent_id", "kb_id", name="uq_agent_kb"),)
    
    # Relationships
    agent = relationship("Agent", back_populates="knowledge_base_associations")
    knowledge_base = relationship("KnowledgeBase", back_populates="agent_associations")


# Workflow Models
class Workflow(Base):
    """Workflow model."""
    
    __tablename__ = "workflows"
    
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    process_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="sequential"
    )  # sequential, hierarchical
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    workflow_agents = relationship("WorkflowAgent", back_populates="workflow")
    tasks = relationship("Task", back_populates="workflow")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowAgent(Base):
    """Workflow-Agent association model (agent instance within a workflow)."""
    
    __tablename__ = "workflow_agents"
    
    workflow_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.workflow_id"),
        nullable=False
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.agent_id"),
        nullable=False
    )
    alias_in_workflow: Mapped[Optional[str]] = mapped_column(String(255))  # User-friendly naming
    sequence_order: Mapped[Optional[int]] = mapped_column(Integer)  # For UI ordering
    
    # Relationships
    workflow = relationship("Workflow", back_populates="workflow_agents")
    agent = relationship("Agent", back_populates="workflow_agents")
    assigned_tasks = relationship("Task", back_populates="assigned_workflow_agent")


class Task(Base):
    """Task model."""
    
    __tablename__ = "tasks"
    
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.workflow_id"),
        nullable=False
    )
    assigned_workflow_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_agents.workflow_agent_id"),
        nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    context_task_ids: Mapped[list] = mapped_column(
        JSONB,
        default=list
    )  # Array of task_ids this task depends on
    human_input_required: Mapped[bool] = mapped_column(Boolean, default=False)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict)  # Task-specific configurations
    
    # Relationships
    workflow = relationship("Workflow", back_populates="tasks")
    assigned_workflow_agent = relationship("WorkflowAgent", back_populates="assigned_tasks")
    executions = relationship("TaskExecution", back_populates="task")


# Execution Monitoring Models
class WorkflowExecution(Base):
    """Workflow Execution model."""
    
    __tablename__ = "workflow_executions"
    
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.workflow_id"),
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column()
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )  # pending, running, completed, failed, cancelled
    inputs_json: Mapped[dict] = mapped_column(JSONB, default=dict)  # Initial inputs
    final_output_json: Mapped[Optional[dict]] = mapped_column(JSONB)  # Final result
    usage_metrics_json: Mapped[Optional[dict]] = mapped_column(JSONB)  # Token counts, etc.
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    user = relationship("User", back_populates="workflow_executions")
    task_executions = relationship("TaskExecution", back_populates="execution")


class TaskExecution(Base):
    """Task Execution model."""
    
    __tablename__ = "task_executions"
    
    task_execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.execution_id"),
        nullable=False
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.task_id"),
        nullable=False
    )  # Original task definition
    assigned_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.agent_id"),
        nullable=False
    )  # Actual agent that ran
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column()
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )  # pending, running, completed, failed
    inputs_data: Mapped[Optional[dict]] = mapped_column(JSONB)  # Input to the task
    output_data: Mapped[Optional[str]] = mapped_column(Text)  # Output of the task agent
    logs_text: Mapped[Optional[str]] = mapped_column(Text)  # Detailed logs
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="task_executions")
    task = relationship("Task", back_populates="executions")
    assigned_agent = relationship("Agent", back_populates="task_executions") 