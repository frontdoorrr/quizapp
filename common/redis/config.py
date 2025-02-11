from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    
    # 캐시 관련 설정
    CACHE_TTL: int = 3600  # 1시간
    
    # 큐 관련 설정
    QUEUE_NAME: str = "score_calculation"
    QUEUE_TIMEOUT: int = 3600  # 1시간

    # 이메일 인증 관련 설정
    EMAIL_VERIFICATION_TTL: int = 86400  # 24시간
