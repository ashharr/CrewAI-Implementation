#!/usr/bin/env python3
"""
Development startup script for the AI Agent Platform.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.shared.database.base import create_tables
from src.shared.utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def setup_database():
    """Set up the database tables."""
    try:
        logger.info("Creating database tables...")
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise


def start_services():
    """Start all development services."""
    logger.info("Starting AI Agent Platform development environment...")
    
    # Start Docker services
    logger.info("Starting Docker services...")
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    
    logger.info("Development environment started successfully!")
    logger.info("API Gateway will be available at: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/docs")


async def main():
    """Main startup function."""
    try:
        # Setup database
        await setup_database()
        
        # Start services
        start_services()
        
        logger.info("Setup completed successfully!")
        
    except Exception as e:
        logger.error("Setup failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 