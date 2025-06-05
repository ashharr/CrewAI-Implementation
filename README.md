# AI Agent & Workflow Management Platform

A comprehensive platform for creating, managing, and executing AI agent workflows using crewAI.

## Features

- **Agent Management**: Create and configure AI agents with different roles, goals, and capabilities
- **Workflow Designer**: Visual workflow builder with drag-and-drop interface
- **Knowledge Base**: Upload and manage documents for RAG (Retrieval Augmented Generation)
- **Model Management**: Support for multiple LLM providers (OpenAI, Anthropic, Ollama, etc.)
- **Execution Monitoring**: Real-time tracking and logging of workflow executions
- **Analytics Dashboard**: Performance metrics and usage analytics

## Architecture

The platform follows a microservices architecture with the following services:

- **API Gateway**: Routes requests and handles cross-cutting concerns
- **Auth Service**: User authentication and authorization
- **Agent Service**: Agent CRUD operations and management
- **Workflow Service**: Workflow and task management
- **Model Service**: LLM model configuration management
- **Knowledge Base Service**: Document processing and RAG functionality
- **Orchestration Engine**: crewAI workflow execution
- **Execution Monitoring**: Logging and tracking of executions
- **Analytics Service**: Data aggregation and reporting

## Technology Stack

### Backend
- **FastAPI**: Web framework
- **PostgreSQL**: Primary database
- **ChromaDB**: Vector database for embeddings
- **Redis**: Caching and message broker
- **Celery**: Background task processing
- **SQLAlchemy**: ORM
- **crewAI**: AI agent orchestration

### Frontend
- **React 18**: Frontend framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **React Flow**: Workflow canvas
- **Zustand**: State management
- **React Query**: Data fetching

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Poetry (Python dependency management)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-agent-platform
   ```

2. **Set up the backend**
   ```bash
   # Install Poetry if not already installed
   curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install

   # Activate virtual environment
   poetry shell

   # Set up pre-commit hooks
   pre-commit install
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start services with Docker**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   # Start API Gateway
   uvicorn src.gateway.main:app --reload --port 8000

   # Start individual services (in separate terminals)
   uvicorn src.services.auth.main:app --reload --port 8001
   uvicorn src.services.agents.main:app --reload --port 8002
   # ... etc for other services
   ```

### Development

1. **Run tests**
   ```bash
   pytest
   ```

2. **Code formatting**
   ```bash
   black src/
   flake8 src/
   mypy src/
   ```

3. **Database migrations**
   ```bash
   # Create new migration
   alembic revision --autogenerate -m "description"

   # Apply migrations
   alembic upgrade head
   ```

## API Documentation

Once the services are running, API documentation is available at:
- API Gateway: http://localhost:8000/docs
- Individual services: http://localhost:800X/docs (where X is the service port)

## Project Structure

```
ai-agent-platform/
├── src/
│   ├── services/                 # Microservices
│   │   ├── auth/                # Authentication service
│   │   ├── agents/              # Agent management service
│   │   ├── workflows/           # Workflow management service
│   │   ├── models/              # LLM model management
│   │   ├── knowledge_base/      # Knowledge base service
│   │   ├── orchestration/       # crewAI orchestration engine
│   │   ├── execution_monitoring/ # Execution tracking
│   │   └── analytics/           # Analytics service
│   ├── shared/                  # Shared utilities
│   │   ├── database/            # Database models and utilities
│   │   ├── auth/                # Authentication utilities
│   │   ├── models/              # Shared Pydantic models
│   │   └── utils/               # Common utilities
│   └── gateway/                 # API Gateway
├── frontend/                    # React frontend application
├── tests/                       # Test files
├── alembic/                     # Database migrations
├── docker-compose.yml           # Docker services
├── pyproject.toml              # Python dependencies and config
└── README.md                   # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.
