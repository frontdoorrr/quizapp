from redis import Redis
from typing import Any
import json
from .config import RedisSettings


class RedisClient:
    def __init__(self, settings: RedisSettings = RedisSettings()):
        self._redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        self.settings = settings

    def get(self, key: str) -> Any:
        """캐시에서 값을 가져옴"""
        value = self._redis.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """캐시에 값을 저장"""
        ttl = ttl or self.settings.CACHE_TTL
        self._redis.setex(key, ttl, json.dumps(value))

    def delete(self, key: str) -> None:
        """캐시에서 값을 삭제"""
        self._redis.delete(key)

    def enqueue(self, data: dict) -> None:
        """작업을 큐에 추가"""
        self._redis.lpush(self.settings.QUEUE_NAME, json.dumps(data))

    def dequeue(self) -> dict | None:
        """큐에서 작업을 가져옴"""
        data = self._redis.brpop(
            self.settings.QUEUE_NAME, timeout=self.settings.QUEUE_TIMEOUT
        )
        return json.loads(data[1]) if data else None
