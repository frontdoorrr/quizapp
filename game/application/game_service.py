from datetime import datetime
from ulid import ULID
import pytz
from dependency_injector.wiring import inject

from game.domain.game import Game, GameStatus
from game.domain.repository.game_repo import IGameRepository
from common.redis.client import RedisClient
from datetime import timedelta
from database import SessionLocal


class GameService:
    @inject
    def __init__(self, game_repo: IGameRepository, redis_client: RedisClient):
        self.game_repo = game_repo
        self.redis_client = redis_client
        self.ulid = ULID()

    def create_game(
        self,
        title: str,
        number: int,
        description: str | None = None,
        question: str | None = None,
        answer: str | None = None,
        question_link: str | None = None,
        answer_link: str | None = None,
    ) -> Game:
        """
        Create a new game with the provided details and save it to the repository.

        Args:
            title (str): The title of the game.
            number (int): The game number.
            description (str | None, optional): A brief description of the game.
            question (str | None, optional): The main question of the game.
            answer (str | None, optional): The answer to the main question.
            question_link (str | None, optional): A link related to the question.
            answer_link (str | None, optional): A link related to the answer.

        Returns:
            Game: The created game object.
        """
        now = datetime.now(pytz.timezone("Asia/Seoul"))
        game = Game(
            id=self.ulid.generate(),
            number=number,
            created_at=now,
            modified_at=now,
            opened_at=None,
            closed_at=None,
            title=title,
            description=description,
            status=GameStatus.DRAFT,
            memo=None,
            question=question,
            answer=answer,
            question_link=question_link,
            answer_link=answer_link,
        )
        self.game_repo.save(game)
        return game

    def update_game(
        self,
        id: str,
        title: str | None = None,
        description: str | None = None,
        question: str | None = None,
        answer: str | None = None,
        question_link: str | None = None,
        answer_link: str | None = None,
        status: GameStatus | None = None,
    ):
        game = self.game_repo.find_by_id(id)
        if title:
            game.title = title
        if description:
            game.description = description
        if question:
            game.question = question
        if answer:
            game.answer = answer
        if question_link:
            game.question_link = question_link
        if answer_link:
            game.answer_link = answer_link
        if status:
            game.status = status

        game.modified_at = datetime.now(pytz.timezone("Asia/Seoul"))

        self.game_repo.update(game)
        return game

    def get_game(self, id: str) -> Game:
        """Get a game by id

        Args:
            id (str): Game id

        Returns:
            Game: Game with given id

        Raises:
            Exception: If game not found
        """
        game = self.game_repo.find_by_id(id)
        if not game:
            raise Exception(f"Game { id} not found")
        return game

    def get_games(self, status: GameStatus | None = None) -> list[Game]:
        """Get games with optional status filter

        Args:
            status (GameStatus | None, optional): Game status filter. Defaults to None.

        Returns:
            list[Game]: List of games with the specified status, or all games if status is None
        """
        if status:
            return self.game_repo.find_by_status(status)
        return self.game_repo.find_all()

    def get_current_game(self) -> Game:
        # """Get the game with the highest number (most recent)

        # Returns:
        #     Game: The most recent game

        # Raises:
        #     Exception: If no games found
        # """
        game = self.game_repo.find_latest()
        if not game:
            raise Exception("No current active game found")
        return game

    def update_game_closing_time(self, game_id: str, closed_at: datetime):
        game = self.game_repo.find_by_id(game_id)
        if not game:
            raise ValueError(f"Game not found: {game_id}")
        game.closed_at = closed_at
        self.game_repo.update(game)
        return game

    def close_game(self, game_id: str) -> Game:
        """게임을 종료하고 점수 계산을 큐에 추가"""
        game = self.game_repo.find_by_id(game_id)
        if not game:
            raise ValueError(f"Game not found: {game_id}")

        if game.status == GameStatus.CLOSED:
            raise ValueError("Game is already closed")

        # 게임 상태 업데이트
        game.status = GameStatus.CLOSED
        game.closed_at = datetime.now(pytz.timezone("Asia/Seoul")) + timedelta(hours=2)
        self.game_repo.update(game)

        # 점수 계산 작업을 큐에 추가
        self.redis_client.enqueue({"game_id": game_id})

        return game

    def delete_game(self, game_id: str) -> Game:
        game = self.game_repo.find_by_id(game_id)
        if not game:
            raise ValueError(f"Game not found: {game_id}")
        
        # 게임과 관련된 답변 삭제
        with SessionLocal() as db:
            from answer.infra.db_models.answer import Answer
            # 관련된 답변 먼저 삭제
            db.query(Answer).filter(Answer.game_id == game_id).delete()
            db.commit()
            
        self.game_repo.delete(game)
        return game
