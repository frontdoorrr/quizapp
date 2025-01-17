from datetime import datetime
from ulid import ULID

from dependency_injector.wiring import inject

from answer.domain.answer import Answer
from answer.domain.repository.answer_repo import IAnswerRepository
from game.domain.repository.game_repo import IGameRepository
from user.domain.repository.user_repo import IUserRepository


class AnswerService:
    @inject
    def __init__(
        self,
        answer_repo: IAnswerRepository,
        game_repo: IGameRepository,
        user_repo: IUserRepository,
    ):
        self.answer_repo = answer_repo
        self.game_repo = game_repo
        self.user_repo = user_repo
        self.ulid = ULID()

    def submit_answer(self, game_id: str, user_id: str, answer_text: str) -> Answer:
        # 게임 정보 조회
        game = self.game_repo.find_by_id(game_id)

        # 정답 여부 확인
        is_correct = game.answer.strip().lower() == answer_text.strip().lower()

        # 포인트 계산 (임시로 정답이면 10점)
        # point = 10 if is_correct else 0

        now = datetime.now()
        answer = Answer(
            id=self.ulid.generate(),
            game_id=game_id,
            user_id=user_id,
            answer=answer_text,
            is_correct=is_correct,
            solved_at=now if is_correct else None,
            created_at=now,
            updated_at=now,
            point=point,
        )

        user = self.user_repo.find_by_id(user_id)
        user.coin

        return self.answer_repo.save(answer)

    def get_answer(self, id: str) -> Answer:
        return self.answer_repo.find_by_id(id)

    def get_answers_by_game(self, game_id: str) -> list[Answer]:
        return self.answer_repo.find_by_game_id(game_id)

    def get_answers_by_user(self, user_id: str) -> list[Answer]:
        return self.answer_repo.find_by_user_id(user_id)

    def get_answer_by_game_and_user(self, game_id: str, user_id: str) -> Answer:
        return self.answer_repo.find_by_game_id_and_user_id(game_id, user_id)
