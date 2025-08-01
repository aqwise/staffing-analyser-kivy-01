"""Application configuration settings"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    app_name: str = "Staffing Analyzer API"
    version: str = "1.0.0"
    debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Google API Configuration
    google_api_key: Optional[str] = None

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
