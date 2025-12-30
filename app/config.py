"""
Application Configuration
Environment variables and settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "CRM SAAS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/crm.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Allowed Hosts - Security Configuration
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    ]
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
    ]
    
    # Worker Configuration - For scaling with multiple workers
    WORKERS: int = 1  # Number of worker processes (use 2-4 * CPU cores in production)
    WORKER_CLASS: str = "uvicorn.workers.UvicornWorker"
    WORKER_TIMEOUT: int = 120  # seconds
    KEEP_ALIVE: int = 5  # seconds
    
    # Background Tasks Configuration
    BACKGROUND_TASK_ENABLED: bool = True
    TASK_QUEUE_SIZE: int = 100
    TASK_RETRY_COUNT: int = 3
    TASK_RETRY_DELAY: int = 60  # seconds
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # requests per window
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Password hashing
    PWD_SCHEME: str = "bcrypt"
    PWD_DEPRECATED: str = "auto"
    
    # Email Configuration (for background email tasks)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@crmsaas.com"
    
    # WhatsApp Configuration
    WHATSAPP_API_URL: Optional[str] = None
    WHATSAPP_API_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

