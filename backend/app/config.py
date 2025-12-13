from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    open_router_api_key: str = ""
    database_url: str = "sqlite:///./jobs.db"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields like old GEMINI_API_KEY


@lru_cache()
def get_settings() -> Settings:
    return Settings()
