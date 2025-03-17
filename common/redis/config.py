from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 다른 환경 변수는 무시
    )

    # Redis settings only
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    EMAIL_VERIFICATION_TTL: int = 300  # 5 minutes
    CACHE_TTL: int = 3600  # 1 hour
    QUEUE_NAME: str = "tasks_queue"
    QUEUE_TIMEOUT: int = 0  # 0은 무한 대기
