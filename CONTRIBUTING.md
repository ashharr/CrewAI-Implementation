# 🤝 Contributing to CrewAI Platform

Thank you for your interest in contributing to the CrewAI Platform! This guide will help you get started with contributing workflows, tools, integrations, and other improvements.

## 🎯 Ways to Contribute

### 1. 🔨 New Workflows
Create specialized workflows for different use cases:
- **Business Workflows**: Sales, marketing, customer service
- **Technical Workflows**: Code analysis, documentation, testing
- **Creative Workflows**: Content creation, design, storytelling
- **Research Workflows**: Market analysis, academic research, competitive intelligence

### 2. 🛠️ Custom Tools
Build tools that extend the platform's capabilities:
- **API Integrations**: Connect to external services
- **Data Processing**: Transform and analyze data
- **Communication**: Send emails, messages, notifications
- **File Handling**: Read, write, convert files

### 3. 🔗 Service Integrations
Connect popular services and platforms:
- **CRM Systems**: Salesforce, HubSpot, Pipedrive
- **Social Media**: Twitter, LinkedIn, Instagram
- **Cloud Platforms**: AWS, Google Cloud, Azure
- **Databases**: PostgreSQL, MongoDB, Redis

### 4. 📚 Documentation
Improve guides and documentation:
- **Tutorials**: Step-by-step guides
- **Examples**: Real-world use cases
- **API Documentation**: Technical references
- **Best Practices**: Guidelines and recommendations

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+** installed on your system
2. **Git** for version control
3. **UV Package Manager** (recommended)
4. **API Keys** for testing your contributions

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/crewai-platform.git
cd crewai-platform

# Create a development branch
git checkout -b feature/your-feature-name

# Install dependencies
source $HOME/.local/bin/env && crewai install

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 📁 Project Structure for Contributors

```
crewai-platform/
├── src/
│   ├── workflows/                 # 🔨 Add your workflows here
│   │   ├── content_creation/      # Content generation workflows
│   │   ├── research/              # Research workflows
│   │   ├── data_processing/       # Data analysis workflows
│   │   └── custom/                # Your custom workflows
│   ├── integrations/              # 🔗 Add integrations here
│   │   ├── apis/                  # API connectors
│   │   ├── databases/             # Database connectors
│   │   └── cloud_services/        # Cloud integrations
│   └── tools/                     # 🛠️ Add custom tools here
├── community/                      # 🤝 Community contributions
│   ├── workflows/                 # Community workflows
│   ├── tools/                     # Community tools
│   └── integrations/              # Community integrations
├── examples/                       # 📖 Add examples here
└── docs/                          # 📚 Documentation
```

## 🔨 Creating a New Workflow

### Step 1: Create Workflow Directory

```bash
mkdir src/workflows/your_workflow_name
cd src/workflows/your_workflow_name
```

### Step 2: Create Required Files

```bash
touch __init__.py
touch crew.py
touch main.py
mkdir config
touch config/agents.yaml
touch config/tasks.yaml
```

### Step 3: Define Your Agents

Create `config/agents.yaml`:

```yaml
# agents.yaml
primary_agent:
  role: "Your Agent Role"
  goal: "What your agent aims to achieve"
  backstory: >
    Detailed background about your agent's expertise,
    experience, and personality traits.

secondary_agent:
  role: "Supporting Agent Role"
  goal: "Supporting objectives"
  backstory: >
    Background for your supporting agent.
```

### Step 4: Define Your Tasks

Create `config/tasks.yaml`:

```yaml
# tasks.yaml
main_task:
  description: >
    Detailed description of what this task should accomplish.
    Include specific requirements and constraints.
  expected_output: >
    Clear description of the expected output format and content.
  agent: primary_agent

follow_up_task:
  description: >
    Description of the follow-up task that uses output from main_task.
  expected_output: >
    Expected output for this task.
  agent: secondary_agent
```

### Step 5: Implement Your Crew

Create `crew.py`:

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool  # Import relevant tools

@CrewBase
class YourWorkflowCrew():
    """Your Workflow Description"""
    
    @agent
    def primary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['primary_agent'],
            verbose=True,
            tools=[SerperDevTool()],  # Add relevant tools
            max_iter=3,  # Optional: limit iterations
            memory=True  # Optional: enable memory
        )
    
    @agent
    def secondary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['secondary_agent'],
            verbose=True
        )
    
    @task
    def main_task(self) -> Task:
        return Task(
            config=self.tasks_config['main_task'],
            # Optional: add callbacks or dependencies
        )
    
    @task
    def follow_up_task(self) -> Task:
        return Task(
            config=self.tasks_config['follow_up_task'],
            # Optional: specify output file
            output_file='output.md'
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # or Process.hierarchical
            verbose=True,
            # Optional: add custom configurations
            max_rpm=10,  # Rate limiting
            memory=True,  # Enable crew memory
            embedder={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            }
        )
```

### Step 6: Create Entry Point

Create `main.py`:

```python
from datetime import datetime
from .crew import YourWorkflowCrew

def run(inputs=None):
    """Run the workflow with optional inputs"""
    default_inputs = {
        'topic': 'Default Topic',
        'current_year': str(datetime.now().year),
        # Add your workflow-specific inputs
    }
    
    # Merge default inputs with provided inputs
    if inputs:
        default_inputs.update(inputs)
    
    result = YourWorkflowCrew().crew().kickoff(inputs=default_inputs)
    return result

def train(n_iterations=3, filename='training_data.pkl'):
    """Train the workflow for better performance"""
    inputs = {
        'topic': 'Training Topic',
        'current_year': str(datetime.now().year)
    }
    
    try:
        YourWorkflowCrew().crew().train(
            n_iterations=n_iterations,
            filename=filename,
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"Training failed: {e}")

if __name__ == "__main__":
    run()
```

### Step 7: Add Documentation

Create `README.md` in your workflow directory:

```markdown
# Your Workflow Name

## Overview
Brief description of what your workflow does.

## Use Cases
- Use case 1
- Use case 2
- Use case 3

## Configuration
Required API keys and setup instructions.

## Usage
```python
from src.workflows.your_workflow_name.main import run

result = run({
    'topic': 'Your Topic',
    'custom_param': 'Custom Value'
})
```

## Output
Description of what the workflow produces.
```

## 🛠️ Creating Custom Tools

### Tool Template

```python
from crewai_tools import BaseTool
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
import requests

class YourCustomToolSchema(BaseModel):
    """Input schema for your custom tool."""
    query: str = Field(..., description="The search query or input parameter")
    additional_param: Optional[str] = Field(None, description="Optional parameter")

class YourCustomTool(BaseTool):
    name: str = "Your Custom Tool"
    description: str = "Clear description of what your tool does"
    args_schema: Type[BaseModel] = YourCustomToolSchema
    
    def _run(self, query: str, additional_param: Optional[str] = None) -> str:
        """
        Execute the tool logic.
        
        Args:
            query: The main input parameter
            additional_param: Optional additional parameter
            
        Returns:
            String result of the tool execution
        """
        try:
            # Your tool logic here
            result = self._execute_tool_logic(query, additional_param)
            return result
        except Exception as e:
            return f"Error executing tool: {str(e)}"
    
    def _execute_tool_logic(self, query: str, additional_param: Optional[str] = None) -> str:
        """Implement your tool's main logic here."""
        # Example: API call
        response = requests.get(f"https://api.example.com/search", 
                              params={"q": query, "param": additional_param})
        return response.json()
```

## 🔗 Creating Service Integrations

### Integration Template

```python
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    """Configuration for your service integration."""
    api_key: str
    base_url: str
    timeout: int = 30

class YourServiceIntegration:
    """Integration with Your Service."""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        })
    
    def create_resource(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource in the service."""
        response = self.session.post(
            f"{self.config.base_url}/resources",
            json=data,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Retrieve a resource from the service."""
        response = self.session.get(
            f"{self.config.base_url}/resources/{resource_id}",
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def list_resources(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List resources with optional filters."""
        params = filters or {}
        response = self.session.get(
            f"{self.config.base_url}/resources",
            params=params,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()
```

## ✅ Testing Your Contribution

### Unit Tests

Create `test_your_contribution.py`:

```python
import pytest
from unittest.mock import Mock, patch
from src.workflows.your_workflow_name.crew import YourWorkflowCrew

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
        inputs = {'topic': 'Test Topic', 'current_year': '2024'}
        
        # Mock the crew execution
        with patch.object(crew.crew(), 'kickoff') as mock_kickoff:
            mock_kickoff.return_value = "Test Result"
            result = crew.crew().kickoff(inputs=inputs)
            assert result == "Test Result"

# Run tests with: python -m pytest test_your_contribution.py
```

### Integration Tests

```python
import pytest
from src.workflows.your_workflow_name.main import run

@pytest.mark.integration
def test_workflow_integration():
    """Integration test for the complete workflow."""
    inputs = {
        'topic': 'AI Development',
        'current_year': '2024'
    }
    
    result = run(inputs)
    assert result is not None
    # Add more specific assertions based on your workflow
```

## 📋 Submission Guidelines

### Before Submitting

1. **✅ Test Your Code**: Ensure all tests pass
2. **✅ Follow Code Style**: Use consistent formatting (run `black` and `flake8`)
3. **✅ Add Documentation**: Include README and inline comments
4. **✅ Update Dependencies**: Add any new dependencies to `pyproject.toml`
5. **✅ Add Examples**: Provide usage examples

### Pull Request Process

1. **Create a Pull Request** with a clear title and description
2. **Fill out the PR template** with:
   - What your contribution does
   - How to test it
   - Any breaking changes
   - Screenshots/examples if applicable

3. **Link Related Issues** if your PR addresses existing issues

4. **Request Review** from maintainers

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] New workflow
- [ ] New tool
- [ ] New integration
- [ ] Bug fix
- [ ] Documentation update
- [ ] Other (please describe)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Documentation
- [ ] README updated
- [ ] Code comments added
- [ ] Examples provided

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Dependencies updated if needed
- [ ] Tests pass locally
```

## 🏆 Recognition

Contributors will be recognized through:

- 🌟 **README Credits**: Listed in our contributors section
- 🎯 **Feature Highlights**: Showcased in our documentation
- 🤝 **Collaboration Opportunities**: Invited to contribute to core features
- 📱 **Social Recognition**: Featured on our social media

## 🆘 Getting Help

### Community Support

- 💬 **GitHub Discussions**: Ask questions and share ideas
- 🐛 **GitHub Issues**: Report bugs or request features
- 📧 **Email**: contact@crewai-platform.com for private inquiries

### Development Help

- 📖 **Documentation**: Check our comprehensive guides
- 🔍 **Code Examples**: Browse existing workflows and tools
- 🤝 **Mentorship**: Pair with experienced contributors

## 📄 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the CrewAI Platform! Your contributions help make AI accessible to everyone. 🚀 