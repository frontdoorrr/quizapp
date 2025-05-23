from datetime import datetime
import pytz
from ulid import ULID

from dependency_injector.wiring import inject

from answer.domain.answer import Answer, AnswerStatus
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

    def create_answer(
        self, game_id: str, user_id: str, answer_text: str = ""
    ) -> Answer:
        return self.answer_repo.save(
            Answer(
                id=self.ulid.generate(),
                game_id=game_id,
                user_id=user_id,
                answer=answer_text,
                is_correct=False,
                solved_at=None,
                created_at=datetime.now(pytz.timezone("Asia/Seoul")),
                updated_at=datetime.now(pytz.timezone("Asia/Seoul")),
                point=0,
                status=AnswerStatus.NOT_USED,
            )
        )

    def create_answer_for_all_users_per_game(
        self,
        game_id: str,
        count: int = 1,
    ):
        users = self.user_repo.find_all()  # TODO 활성화된 user 대상으로만 좁혀야 함
        now = datetime.now(pytz.timezone("Asia/Seoul"))
        for _ in range(count):
            for user in users:
                # TODO bulk하여 save할지 고민 필요
                self.answer_repo.save(
                    Answer(
                        id=self.ulid.generate(),
                        game_id=game_id,
                        user_id=user.id,
                        answer="-",
                        is_correct=False,
                        solved_at=None,
                        created_at=now,
                        updated_at=now,
                        point=0,
                        status=AnswerStatus.NOT_USED,
                    )
                )

        return True

    def submit_answer(self, game_id: str, user_id: str, answer_text: str) -> Answer:
        # 게임 정보 조회
        game = self.game_repo.find_by_id(game_id)

        # 유저 정보 조회
        user = self.user_repo.find_by_id(user_id)
        # if user.coin < 1:
        #     raise InsufficientCoinError()

        # 정답 여부 확인
        is_correct = game.answer.strip().lower() == answer_text.strip().lower()

        # 포인트 계산 (임시로 정답이면 10점)
        # point = 10 if is_correct else 0

        now = datetime.now(pytz.timezone("Asia/Seoul"))
        # answer = Answer(
        #     id=self.ulid.generate(),
        #     game_id=game_id,
        #     user_id=user_id,
        #     answer=answer_text,
        #     is_correct=is_correct,
        #     solved_at=now if is_correct else None,
        #     created_at=now,
        #     updated_at=now,
        #     point=0,
        #     status=AnswerStatus.SUBMITTED,
        # )
        answer = self.answer_repo.find_not_used_by_game_id_and_user_id(game_id, user_id)

        if answer:
            answer.answer = answer_text
            answer.is_correct = is_correct
            answer.solved_at = now if is_correct else None
            answer.updated_at = now
            answer.status = AnswerStatus.SUBMITTED
        else:
            raise HTTPException(
                status_code=400,
                detail="Already used all the chances provided",
            )

        self.user_repo.update(user)

        return self.answer_repo.update(answer)

    def update_answer(self, id: str, answer: Answer) -> Answer:
        # 기존 답변 확인
        existing_answer = self.answer_repo.find_by_id(id)
        if not existing_answer:
            raise ValueError(f"Answer not found: {id}")
            
        # 답변 내용 업데이트
        existing_answer.answer = answer.answer
        existing_answer.point = answer.point
        existing_answer.updated_at = datetime.now(pytz.timezone("Asia/Seoul"))
        
        # 저장
        return self.answer_repo.update(existing_answer)

    def get_answer(self, id: str) -> Answer:
        return self.answer_repo.find_by_id(id)

    def get_answers_by_game(self, game_id: str) -> list[Answer]:
        return self.answer_repo.find_by_game_id(game_id)

    def get_answers_by_user(self, user_id: str) -> list[Answer]:
        return self.answer_repo.find_by_user_id(user_id)

    def get_unused_answers_by_game_and_user(
        self, game_id: str, user_id: str
    ) -> list[Answer] | Answer:
        return self.answer_repo.find_unused_by_game_id_and_user_id(game_id, user_id)

    def get_corrected_answer_by_game_and_user(
        self, game_id: str, user_id: str
    ) -> Answer:
        return self.answer_repo.find_corrected_by_game_id_and_user_id(game_id, user_id)

    def get_corrected_answers_by_game(self, game_id: str, limit: int = 10) -> list[Answer]:
        return self.answer_repo.find_corrected_by_game_id(game_id, limit=limit)

    def delete_answer_by_game_and_user(self, game_id: str, user_id: str) -> None:
        """Delete answer by game_id and user_id

        Args:
            game_id (str): Game ID
            user_id (str): User ID

        Raises:
            ValueError: If answer not found
        """
        # TODO
        # answer = self.get_answer_by_game_and_user(game_id, user_id)

        if not answer:
            raise ValueError(
                f"Answer not found for game_id: {game_id} and user_id: {user_id}"
            )
        self.answer_repo.delete_by_id(answer.id)

    def calculate_points(self, game_id: str, multiplier: int = 50):
        corrected_answers = self.get_corrected_answers_by_game(game_id)

        # 점수 계산 로직
        
        length = len(corrected_answers)


        for idx, answer in enumerate(corrected_answers):
            rank = idx + 1

            if answer.is_correct:
                answer.point = round(multiplier * ((1 - (2 / length)) ** rank))
            self.answer_repo.update(answer)
    
    def update_total_user_point(self, game_id: str):
        corrected_answers = self.get_corrected_answers_by_game(game_id, limit=100)
        for corrected_answer in corrected_answers:
            user_id = corrected_answer.user_id
            answers = self.get_answers_by_user(user_id)
            total_point = sum(answer.point for answer in answers)
            user = self.user_repo.find_by_id(user_id)
            user.point = total_point
            self.user_repo.update(user)
            
        
        
        