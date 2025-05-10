from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import pytz
from common.redis.client import RedisClient
from common.auth import decode_access_token
from containers import Container

class ActiveUserMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        container = Container()
        self.redis_client = container.redis_client()
        self.user_activity_prefix = "user_activity:"
        self.active_users_count_key = "active_users_count"
        self.ttl = 300  # 300초(5분) 동안 활성 사용자로 간주

    async def dispatch(self, request: Request, call_next):
        # 인증된 요청인지 확인
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                # 토큰 디코딩
                payload = decode_access_token(token)
                user_id = payload.get("sub")
                
                if user_id:
                    # 사용자 활동 시간 업데이트
                    now = datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
                    user_key = f"{self.user_activity_prefix}{user_id}"
                    
                    # Redis에 사용자 활동 정보 저장
                    self.redis_client.set(user_key, {"last_activity": now}, self.ttl)
            except Exception as e:
                # 토큰 디코딩 실패 시 무시
                pass
                
        # 요청 처리 후 응답 반환
        response = await call_next(request)
        return response
    
    def get_active_users_count(self) -> int:
        """현재 활성 사용자 수를 계산하여 반환"""
        # Redis의 키 패턴으로 활성 사용자 키를 모두 조회
        keys = self.redis_client._redis.keys(f"{self.user_activity_prefix}*")
        count = len(keys)
        
        # 캐시에 저장 (60초 TTL)
        self.redis_client.set(self.active_users_count_key, count, 60)
        return count
    
    def get_cached_active_users_count(self) -> int:
        """캐시된 활성 사용자 수를 반환"""
        count = self.redis_client.get(self.active_users_count_key)
        if count is None:
            # 캐시에 없으면 새로 계산
            return self.get_active_users_count()
        return count
