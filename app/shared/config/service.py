"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_file=".env")
    
    app_name: str = "Octopus App"
    environment: str = "development"
    database_url: str | None = None


# Global settings instance
settings = Settings()
