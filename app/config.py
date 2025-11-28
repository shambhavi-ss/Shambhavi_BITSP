from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application level configuration sourced from env or defaults."""

    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    tesseract_cmd: Optional[str] = None
    poppler_path: Optional[str] = None
    temp_dir: Path = Path("tmp")
    request_timeout_seconds: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    return settings

