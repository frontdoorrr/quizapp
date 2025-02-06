import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.redis.client import RedisClient
from common.redis.config import RedisSettings
from game.domain.repository.game_repo import IGameRepository
from answer.domain.repository.answer_repo import IAnswerRepository
from user.domain.repository.user_repo import IUserRepository
from containers import Container
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoreCalculationWorker:
    def __init__(
        self,
        redis_client: RedisClient,
        game_repo: IGameRepository,
        answer_repo: IAnswerRepository,
        user_repo: IUserRepository
    ):
        self.redis_client = redis_client
        self.game_repo = game_repo
        self.answer_repo = answer_repo
        self.user_repo = user_repo
    
    def calculate_score(self, game_id: str) -> None:
        """게임의 점수를 계산하고 사용자 포인트를 업데이트"""
        try:
            # 게임 정보 조회
            game = self.game_repo.find_by_id(game_id)
            if not game:
                logger.error(f"Game not found: {game_id}")
                return
            
            # 해당 게임의 모든 답변 조회
            answers = self.answer_repo.find_by_game_id(game_id)
            
            for answer in answers:
                # 정답 여부 확인
                is_correct = game.answer.strip().lower() == answer.answer_text.strip().lower()
                points = 10 if is_correct else 0  # 임시로 정답이면 10점
                
                # 사용자 포인트 업데이트
                user = self.user_repo.find_by_id(answer.user_id)
                if user:
                    user.point += points
                    self.user_repo.update(user)
                    logger.info(f"Updated points for user {user.id}: +{points}")
                
                # 답변 포인트 업데이트
                answer.point = points
                self.answer_repo.update(answer)
            
            logger.info(f"Score calculation completed for game {game_id}")
            
        except Exception as e:
            logger.error(f"Error calculating score for game {game_id}: {str(e)}")
    
    def run(self):
        """워커 실행"""
        logger.info("Score calculation worker started")
        while True:
            try:
                # 큐에서 작업 가져오기
                data = self.redis_client.dequeue()
                if data and 'game_id' in data:
                    logger.info(f"Processing score calculation for game {data['game_id']}")
                    self.calculate_score(data['game_id'])
                
                time.sleep(1)  # 부하 방지를 위한 대기
                
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                time.sleep(5)  # 에러 발생시 더 긴 대기

def main():
    # 컨테이너 초기화
    container = Container()
    container.init_resources()
    
    # 워커 인스턴스 생성
    worker = ScoreCalculationWorker(
        redis_client=container.redis_client(),
        game_repo=container.game_repo(),  # game_repository() -> game_repo()
        answer_repo=container.answer_repo(),  # answer_repository() -> answer_repo()
        user_repo=container.user_repo()  # user_repository() -> user_repo()
    )
    
    # 워커 실행
    worker.run()

if __name__ == "__main__":
    main()
