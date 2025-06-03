# Creating Custom Workflows

This guide will walk you through creating custom workflows for the CrewAI platform. Workflows are the core building blocks that define how multiple AI agents collaborate to accomplish complex tasks.

## 📋 Table of Contents

1. [Workflow Basics](#workflow-basics)
2. [Directory Structure](#directory-structure)
3. [Agent Configuration](#agent-configuration)
4. [Task Definition](#task-definition)
5. [Crew Implementation](#crew-implementation)
6. [Entry Points](#entry-points)
7. [Testing](#testing)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

## 🎯 Workflow Basics

A CrewAI workflow consists of:

- **Agents**: AI entities with specific roles and capabilities
- **Tasks**: Specific jobs that agents need to complete
- **Tools**: External integrations and capabilities agents can use
- **Process**: How tasks are executed (sequential, parallel, hierarchical)

### Workflow Types

1. **Sequential Workflows**: Tasks executed one after another
2. **Parallel Workflows**: Tasks executed simultaneously
3. **Hierarchical Workflows**: Manager agent coordinates other agents

## 📁 Directory Structure

Create your workflow in the appropriate category:

```
src/workflows/
├── content_creation/     # Content generation workflows
├── research/            # Research and analysis workflows
├── data_processing/     # Data analysis workflows
├── custom/              # Your custom workflows
└── your_workflow_name/
    ├── __init__.py
    ├── main.py          # Entry point
    ├── crew.py          # Crew definition
    ├── config/
    │   ├── agents.yaml  # Agent configurations
    │   └── tasks.yaml   # Task definitions
    ├── tools/           # Custom tools (optional)
    ├── tests/           # Unit tests
    └── README.md        # Documentation
```

## 🤖 Agent Configuration

### agents.yaml Structure

```yaml
# Agent name (used as identifier)
agent_name:
  role: >
    Brief description of the agent's role
  goal: >
    What the agent aims to achieve
  backstory: >
    Detailed background that gives the agent personality
    and expertise context
```

### Example Agent Configuration

```yaml
research_specialist:
  role: >
    Senior Research Analyst
  goal: >
    Conduct comprehensive research on {topic} and provide 
    accurate, up-to-date information with credible sources
  backstory: >
    You are an experienced research analyst with 10+ years 
    in market research and data analysis. You have a keen 
    eye for identifying reliable sources and extracting 
    valuable insights from complex information. Your 
    expertise spans multiple industries and you're known 
    for your thorough, fact-based research methodology.

content_writer:
  role: >
    Professional Content Creator
  goal: >
    Transform research findings into engaging, well-structured 
    content that resonates with {target_audience}
  backstory: >
    You are a skilled content writer with expertise in 
    creating compelling narratives across various formats. 
    Your writing is clear, engaging, and always tailored 
    to the specific audience and purpose. You understand 
    SEO principles and how to balance optimization with 
    readability.
```

### Agent Parameters

- **role**: The agent's professional role or title
- **goal**: What the agent is trying to accomplish
- **backstory**: Personality, experience, and expertise
- **{variables}**: Use placeholders for dynamic content

## 📋 Task Definition

### tasks.yaml Structure

```yaml
task_name:
  description: >
    Detailed description of what the task involves.
    Include specific requirements, constraints, and context.
  expected_output: >
    Clear description of the expected output format,
    content, and quality standards.
  agent: agent_name
  # Optional parameters
  output_file: filename.md
  context: [previous_task_name]
  tools: [tool_name]
```

### Example Task Configuration

```yaml
research_task:
  description: >
    Conduct comprehensive research on "{topic}" focusing on:
    
    1. Current trends and developments in {current_year}
    2. Key statistics and market data
    3. Expert opinions and thought leadership
    4. Case studies and real-world examples
    5. Challenges and opportunities
    
    Target audience: {target_audience}
    
    Requirements:
    - Use credible sources (industry publications, research reports)
    - Include recent data (within last 12 months)
    - Cite all sources properly
    - Focus on actionable insights
  expected_output: >
    A structured research report containing:
    - Executive summary (200 words)
    - 10-15 key findings with source citations
    - Relevant statistics and data points
    - Expert quotes and insights
    - Trending topics and keywords
    - Source credibility assessment
    
    Format as markdown with clear sections and proper citations.
  agent: research_specialist
  output_file: research_findings.md

content_creation_task:
  description: >
    Using the research findings, create engaging content about "{topic}":
    
    Requirements:
    - Word count: {word_count} words
    - Tone: {tone}
    - Target audience: {target_audience}
    - Include key findings from research
    - Use SEO best practices
    - Include call-to-action
  expected_output: >
    A complete, publication-ready article with:
    - Compelling headline
    - Engaging introduction
    - Well-structured body content
    - Strong conclusion with CTA
    - Proper formatting and readability
  agent: content_writer
  context: [research_task]
  output_file: final_content.md
```

### Task Parameters

- **description**: Detailed task instructions
- **expected_output**: What the agent should produce
- **agent**: Which agent handles this task
- **output_file**: Save output to file (optional)
- **context**: Dependencies on other tasks (optional)
- **tools**: Specific tools for this task (optional)

## 🎭 Crew Implementation

### Basic Crew Structure

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, FileReadTool

@CrewBase
class YourWorkflowCrew():
    """Your Workflow Description"""
    
    @agent
    def research_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['research_specialist'],
            verbose=True,
            tools=[SerperDevTool()],
            max_iter=3,
            memory=True
        )
    
    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer'],
            verbose=True,
            memory=True
        )
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task']
        )
    
    @task
    def content_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_creation_task']
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10,
            memory=True
        )
```

### Advanced Crew Configuration

```python
@crew
def crew(self) -> Crew:
    return Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.sequential,  # or Process.hierarchical
        verbose=True,
        
        # Performance settings
        max_rpm=10,              # Rate limiting
        max_execution_time=3600, # 1 hour timeout
        
        # Memory and learning
        memory=True,
        embedder={
            "provider": "openai",
            "config": {"model": "text-embedding-3-small"}
        },
        
        # Output settings
        output_log_file="crew_execution.log",
        
        # Callbacks (optional)
        step_callback=self._step_callback,
        task_callback=self._task_callback
    )

def _step_callback(self, step):
    """Called after each step"""
    print(f"Step completed: {step}")

def _task_callback(self, task):
    """Called after each task"""
    print(f"Task completed: {task.description[:50]}...")
```

## 🚀 Entry Points

### main.py Template

```python
#!/usr/bin/env python
"""
Your Workflow Name

Brief description of what your workflow does and its use cases.
"""

from datetime import datetime
from .crew import YourWorkflowCrew

def run(inputs=None):
    """
    Run the workflow with optional inputs.
    
    Args:
        inputs (dict): Optional input parameters
            - param1 (str): Description
            - param2 (int): Description
    
    Returns:
        CrewOutput: The workflow results
    """
    default_inputs = {
        'topic': 'Default Topic',
        'target_audience': 'General audience',
        'current_year': str(datetime.now().year)
    }
    
    if inputs:
        default_inputs.update(inputs)
    
    print(f"🚀 Starting workflow: {default_inputs['topic']}")
    
    result = YourWorkflowCrew().crew().kickoff(inputs=default_inputs)
    
    print("✅ Workflow completed!")
    return result

def train(n_iterations=3, filename='training_data.pkl'):
    """Train the workflow for better performance."""
    inputs = {
        'topic': 'Training Topic',
        'target_audience': 'Training audience',
        'current_year': str(datetime.now().year)
    }
    
    try:
        print(f"🎓 Training workflow for {n_iterations} iterations...")
        YourWorkflowCrew().crew().train(
            n_iterations=n_iterations,
            filename=filename,
            inputs=inputs
        )
        print("✅ Training completed!")
    except Exception as e:
        raise Exception(f"Training failed: {e}")

if __name__ == "__main__":
    # Example usage
    sample_inputs = {
        'topic': 'AI in Healthcare',
        'target_audience': 'Healthcare professionals'
    }
    
    run(sample_inputs)
```

## 🧪 Testing

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch
from src.workflows.your_workflow.crew import YourWorkflowCrew

class TestYourWorkflow:
    
    def test_crew_creation(self):
        """Test that the crew can be created successfully."""
        crew = YourWorkflowCrew()
        assert crew is not None
        
    def test_agents_configuration(self):
        """Test that agents are configured correctly."""
        crew = YourWorkflowCrew()
        agents = crew.agents
        assert len(agents) > 0
        
    @patch('crewai_tools.SerperDevTool')
    def test_workflow_execution(self, mock_tool):
        """Test that the workflow executes without errors."""
        mock_tool.return_value = Mock()
        
        crew = YourWorkflowCrew()
        inputs = {'topic': 'Test Topic'}
        
        with patch.object(crew.crew(), 'kickoff') as mock_kickoff:
            mock_kickoff.return_value = "Test Result"
            result = crew.crew().kickoff(inputs=inputs)
            assert result == "Test Result"
```

## 🎯 Best Practices

### 1. Agent Design

- **Specific Roles**: Give agents clear, specific roles
- **Realistic Backstories**: Create believable expertise
- **Appropriate Tools**: Only give agents tools they need
- **Memory Management**: Use memory for complex workflows

### 2. Task Design

- **Clear Instructions**: Be specific about requirements
- **Expected Output**: Define exactly what you want
- **Context Dependencies**: Use task context for sequential workflows
- **Error Handling**: Plan for failure scenarios

### 3. Performance Optimization

- **Rate Limiting**: Use `max_rpm` to avoid API limits
- **Timeouts**: Set reasonable execution timeouts
- **Tool Selection**: Choose efficient tools
- **Memory Usage**: Monitor memory consumption

### 4. Error Handling

```python
def run(inputs=None):
    try:
        result = YourWorkflowCrew().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        # Log error details
        # Send notifications if needed
        raise
```

### 5. Monitoring and Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run(inputs=None):
    logger.info(f"Starting workflow with inputs: {inputs}")
    
    try:
        result = YourWorkflowCrew().crew().kickoff(inputs=inputs)
        logger.info("Workflow completed successfully")
        return result
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}")
        raise
```

## 📚 Examples

### Simple Research Workflow

A basic workflow that researches a topic and creates a summary:

```python
# Agents: researcher, summarizer
# Tasks: research_task, summary_task
# Process: sequential
```

### Content Marketing Pipeline

A comprehensive content creation workflow:

```python
# Agents: researcher, seo_specialist, writer, editor
# Tasks: research, seo_analysis, content_creation, editing
# Process: sequential with context passing
```

### Data Analysis Workflow

A workflow for analyzing and reporting on data:

```python
# Agents: data_analyst, statistician, report_writer
# Tasks: data_collection, analysis, visualization, reporting
# Process: sequential with file outputs
```

## 🔗 Next Steps

1. **Create Your First Workflow**: Start with a simple 2-agent workflow
2. **Test Thoroughly**: Write unit tests and integration tests
3. **Document Everything**: Create clear README and examples
4. **Share with Community**: Submit a pull request
5. **Iterate and Improve**: Gather feedback and enhance

## 📞 Getting Help

- **Documentation**: Check our comprehensive guides
- **Examples**: Browse existing workflows for inspiration
- **Community**: Join our Discord for questions
- **Issues**: Report bugs or request features on GitHub

Happy workflow building! 🚀 