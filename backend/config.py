from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = ""
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    chroma_persist_dir: str = "./data"
    app_env: str = "development"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
