from common.redis.client import RedisClient
import time
import threading
from datetime import datetime
import pytz

class ActiveUserService:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.user_activity_prefix = "user_activity:"
        self.active_users_count_key = "active_users_count"
        self.active_users_list_key = "active_users_list"
        self.update_interval = 30  # 30초마다 업데이트
        self._running = False
        self._thread = None
    
    def get_active_users_count(self) -> int:
        """현재 활성 사용자 수를 반환"""
        count = self.redis_client.get(self.active_users_count_key)
        if count is None:
            # 캐시에 없으면 새로 계산
            return self._update_active_users_count()
        return count
    
    def get_active_users(self) -> list:
        """현재 활성 사용자 목록을 반환"""
        users = self.redis_client.get(self.active_users_list_key)
        if users is None:
            # 캐시에 없으면 새로 계산
            return self._update_active_users_list()
        return users
    
    def _update_active_users_count(self) -> int:
        """Redis에서 활성 사용자 수를 계산하여 캐시에 저장"""
        # Redis의 키 패턴으로 활성 사용자 키를 모두 조회
        keys = self.redis_client._redis.keys(f"{self.user_activity_prefix}*")
        count = len(keys)
        self.redis_client.set(self.active_users_count_key, count, 60)  # 60초 TTL
        return count
    
    def _update_active_users_list(self) -> list:
        """Redis에서 활성 사용자 목록을 가져와 캐시에 저장"""
        # Redis의 키 패턴으로 활성 사용자 키를 모두 조회
        keys = self.redis_client._redis.keys(f"{self.user_activity_prefix}*")
        
        # 사용자 ID 추출 및 활동 정보 가져오기
        active_users = []
        for key in keys:
            user_id = key.replace(self.user_activity_prefix, "")
            user_data = self.redis_client.get(key)
            if user_data:
                # 사용자 정보 조회 (옵션)
                from user.infra.repository.user_repo import UserRepository
                user_repo = UserRepository()
                user = user_repo.find_by_id(user_id)
                
                if user:
                    active_users.append({
                        "id": user_id,
                        "name": user.name if hasattr(user, 'name') else None,
                        "nickname": user.nickname if hasattr(user, 'nickname') else None,
                        "email": user.email if hasattr(user, 'email') else None,
                        "last_activity": user_data.get("last_activity")
                    })
                else:
                    active_users.append({
                        "id": user_id,
                        "last_activity": user_data.get("last_activity")
                    })
        
        # 캐시에 저장 (60초 TTL)
        self.redis_client.set(self.active_users_list_key, active_users, 60)
        return active_users
    
    def start_background_updater(self):
        """백그라운드에서 활성 사용자 수를 주기적으로 업데이트"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._background_update_task)
        self._thread.daemon = True
        self._thread.start()
    
    def stop_background_updater(self):
        """백그라운드 업데이트 작업 중지"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
    
    def _background_update_task(self):
        """백그라운드에서 실행되는 업데이트 작업"""
        while self._running:
            try:
                self._update_active_users_count()
                self._update_active_users_list()
            except Exception as e:
                print(f"활성 사용자 정보 업데이트 중 오류 발생: {e}")
            time.sleep(self.update_interval)
    
    def record_user_activity(self, user_id: str):
        """사용자 활동 기록"""
        if not user_id:
            return
            
        now = datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
        user_key = f"{self.user_activity_prefix}{user_id}"
        
        # Redis에 사용자 활동 정보 저장 (300초 TTL)
        self.redis_client.set(user_key, {"last_activity": now}, 300)
