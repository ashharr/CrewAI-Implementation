# CrewAI Platform Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy source code
COPY src/ ./src/
COPY docs/ ./docs/
COPY examples/ ./examples/
COPY tests/ ./tests/

# Copy configuration files
COPY .env.example ./
COPY README.md ./
COPY CONTRIBUTING.md ./

# Create necessary directories
RUN mkdir -p /app/outputs /app/logs /app/uploads

# Set permissions
RUN chmod +x /app/src/workflows/*/main.py

# Expose port for web interface (if implemented)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "src.workflows.research.ai_development.main"] 