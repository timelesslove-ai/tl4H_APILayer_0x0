"""
Global application configuration.
Centralizes environment-specific settings and feature flags.
"""
"""
Global application configuration.
Centralizes environment-specific settings and feature flags.
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Core application settings
    APP_NAME: str = "Timeless Love 4H"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        """Build database URI from components if not provided directly"""
        if isinstance(v, str):
            return v
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT", 5432)),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Cloud Storage settings
    STORAGE_PROVIDER: str = "gcp"  # gcp, aws, azure, local
    GCP_PROJECT_ID: Optional[str] = None
    GCP_BUCKET_NAME: Optional[str] = None
    GCP_CREDENTIALS_FILE: Optional[str] = None
    
    # Media processing settings
    UPLOAD_FOLDER: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_MEDIA_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/heic", "image/heif",
        "video/mp4", "video/quicktime", "video/x-msvideo",
        "audio/mpeg", "audio/mp4", "audio/wav",
        "application/pdf", "text/plain"
    ]
    
    # ML settings
    ENABLE_ML_FEATURES: bool = True
    ML_API_URL: Optional[str] = None
    ML_API_KEY: Optional[str] = None
    
    # Notification settings
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_FROM_NAME: Optional[str] = None
    
    # Age Gate settings
    DEFAULT_AGE_GATE_RULES: Dict[str, Any] = {
        "public": {"years": 0, "months": 0, "days": 0},
        "teens": {"years": 13, "months": 0, "days": 0},
        "young_adult": {"years": 18, "months": 0, "days": 0}
    }
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    ENABLE_OPENTELEMETRY: bool = False
    OPENTELEMETRY_ENDPOINT: Optional[str] = None
    
    # Feature flags
    ENABLE_TIMELINE_VIEW: bool = True
    ENABLE_MEMORY_CONNECTIONS: bool = True
    ENABLE_DEVELOPMENTAL_CONTEXT: bool = True
    ENABLE_MILESTONE_TRACKING: bool = True
    
    # Performance settings
    ENABLE_RESPONSE_CACHE: bool = True
    RESPONSE_CACHE_EXPIRE_SECONDS: int = 60 * 5  # 5 minutes
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

