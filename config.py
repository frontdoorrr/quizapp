from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str = "postgresql://postgres:postgres@localhost:5432/quizapp"
    jwt_secret: str


@lru_cache
def get_settings():
    return Settings()
