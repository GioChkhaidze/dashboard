"""
Application Configuration Settings
"""
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Project Info
    PROJECT_NAME: str = "Agricultural Dashboard API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "agri_dashboard"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Field Configuration
    DEFAULT_GRID_SIZE: float = 1.0
    PEST_DENSITY_WARNING_THRESHOLD: float = 5.0
    PEST_DENSITY_CRITICAL_THRESHOLD: float = 10.0
    CANOPY_WARNING_THRESHOLD: float = 60.0
    CANOPY_CRITICAL_THRESHOLD: float = 50.0
    
    # Scheduling
    DAILY_FLIGHT_TIME: str = "07:00"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
