"""
Shared configuration settings for the AI Agent Platform.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(
        default="postgresql+asyncpg://username:password@localhost:5432/ai_agent_platform",
        description="Database connection URL"
    )
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="ai_agent_platform")
    user: str = Field(default="username")
    password: str = Field(default="password")
    
    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = Field(default="redis://localhost:6379/0")
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)
    
    class Config:
        env_prefix = "REDIS_"


class JWTSettings(BaseSettings):
    """JWT configuration settings."""
    
    secret_key: str = Field(default="your-super-secret-jwt-key-change-this-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    
    class Config:
        env_prefix = "JWT_"


class Settings(BaseSettings):
    """Main application settings."""
    
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 