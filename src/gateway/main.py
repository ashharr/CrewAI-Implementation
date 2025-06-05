"""
API Gateway for the AI Agent Platform.
Routes requests to appropriate microservices.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import uuid

from src.shared.config import get_settings
from src.shared.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

settings = get_settings()

app = FastAPI(
    title="AI Agent Platform API Gateway",
    description="API Gateway for the AI Agent & Workflow Management Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to all requests."""
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(
        "Incoming request",
        method=request.method,
        url=str(request.url),
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    
    response = await call_next(request)
    
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    
    return response


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Agent Platform API Gateway", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


# Service routing will be added in subsequent phases
# Example route structure:
# @app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
# async def auth_service_proxy(request: Request, path: str):
#     """Proxy requests to auth service."""
#     # Implementation will be added in Phase 3


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.gateway.main:app",
        host=settings.services.api_gateway_host,
        port=settings.services.api_gateway_port,
        reload=settings.debug,
    ) 