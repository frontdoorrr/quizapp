import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from answer.application.answer_service import AnswerService
from answer.domain.answer import Answer
from answer.infra.repository.answer_repo import AnswerRepository
from game.infra.repository.game_repo import GameRepository
from game.domain.game import Game

from ulid import ULID


class TestAnswerService:
    @pytest.fixture
    def answer_repo_mock(self):
        return Mock(spec=AnswerRepository)

    @pytest.fixture
    def game_repo_mock(self):
        return Mock(spec=GameRepository)

    @pytest.fixture
    def answer_service(self, answer_repo_mock, game_repo_mock):
        return AnswerService(
            answer_repo=answer_repo_mock,
            game_repo=game_repo_mock,
            ulid=ULID()
        )

    @pytest.fixture
    def active_game(self):
        return Game(
            id="01HABCDEFGHJKMNPQRSTUVWXYZ",
            title="Test Game",
            number=1,
            description="Test Description",
            question="Test Question?",
            answer="test answer",
            question_link="https://example.com/question",
            answer_link="https://example.com/answer",
            status="ACTIVE",
            created_at=datetime.now(),
            closed_at=None
        )

    @pytest.fixture
    def closed_game(self):
        return Game(
            id="01HCLOSEDGAMERSTUVWXYZ1234",
            title="Closed Game",
            number=2,
            description="Closed Game Description",
            question="Closed Game Question?",
            answer="closed game answer",
            question_link="https://example.com/closed-question",
            answer_link="https://example.com/closed-answer",
            status="CLOSED",
            created_at=datetime.now() - timedelta(days=1),
            closed_at=datetime.now()
        )

    @pytest.fixture
    def user_answer(self):
        return Answer(
            id="01HANSWER1234567890ABCDEFG",
            game_id="01HABCDEFGHJKMNPQRSTUVWXYZ",
            user_id="01HUSER12345678ABCDEFGHJK",
            answer="test answer",
            is_correct=True,
            score=100,
            submitted_at=datetime.now(),
            created_at=datetime.now()
        )

    def test_create_answer(self, answer_service, game_repo_mock, answer_repo_mock, active_game):
        # 설정
        game_repo_mock.get_by_id.return_value = active_game
        user_id = "01HUSER12345678ABCDEFGHJK"

        # 실행
        result = answer_service.create_answer(
            game_id=active_game.id,
            user_id=user_id
        )

        # 검증
        game_repo_mock.get_by_id.assert_called_once_with(active_game.id)
        answer_repo_mock.save.assert_called_once()
        assert result.id is not None  # 실제 ULID 값이 생성되었는지 확인
        assert len(result.id) > 0  # ID가 비어있지 않은지 확인
        assert result.game_id == active_game.id
        assert result.user_id == user_id
        assert result.answer is None
        assert result.is_correct is None
        assert result.score is None

    def test_create_answer_game_not_found(self, answer_service, game_repo_mock):
        # 설정
        game_repo_mock.get_by_id.return_value = None
        user_id = "01HUSER12345678ABCDEFGHJK"
        game_id = "nonexistent_game_id"

        # 실행 및 검증
        with pytest.raises(Exception):
            answer_service.create_answer(
                game_id=game_id,
                user_id=user_id
            )
        
        game_repo_mock.get_by_id.assert_called_once_with(game_id)

    def test_create_answer_game_closed(self, answer_service, game_repo_mock, closed_game):
        # 설정
        game_repo_mock.get_by_id.return_value = closed_game
        user_id = "01HUSER12345678ABCDEFGHJK"

        # 실행 및 검증
        with pytest.raises(Exception):
            answer_service.create_answer(
                game_id=closed_game.id,
                user_id=user_id
            )
        
        game_repo_mock.get_by_id.assert_called_once_with(closed_game.id)

    def test_submit_answer_correct(self, answer_service, answer_repo_mock, game_repo_mock, active_game, user_answer):
        # 설정
        answer_without_submission = Answer(
            id=user_answer.id,
            game_id=user_answer.game_id,
            user_id=user_answer.user_id,
            answer=None,
            is_correct=None,
            score=None,
            submitted_at=None,
            created_at=user_answer.created_at
        )
        
        answer_repo_mock.get_by_id.return_value = answer_without_submission
        game_repo_mock.get_by_id.return_value = active_game
        
        # 실행
        result = answer_service.submit_answer(
            answer_id=user_answer.id,
            answer_text="test answer"  # 정답
        )

        # 검증
        answer_repo_mock.get_by_id.assert_called_once_with(user_answer.id)
        game_repo_mock.get_by_id.assert_called_once_with(active_game.id)
        answer_repo_mock.save.assert_called_once()
        
        assert result.answer == "test answer"
        assert result.is_correct is True
        assert result.submitted_at is not None

    def test_submit_answer_incorrect(self, answer_service, answer_repo_mock, game_repo_mock, active_game, user_answer):
        # 설정
        answer_without_submission = Answer(
            id=user_answer.id,
            game_id=user_answer.game_id,
            user_id=user_answer.user_id,
            answer=None,
            is_correct=None,
            score=None,
            submitted_at=None,
            created_at=user_answer.created_at
        )
        
        answer_repo_mock.get_by_id.return_value = answer_without_submission
        game_repo_mock.get_by_id.return_value = active_game
        
        # 실행
        result = answer_service.submit_answer(
            answer_id=user_answer.id,
            answer_text="wrong answer"  # 오답
        )

        # 검증
        answer_repo_mock.get_by_id.assert_called_once_with(user_answer.id)
        game_repo_mock.get_by_id.assert_called_once_with(active_game.id)
        answer_repo_mock.save.assert_called_once()
        
        assert result.answer == "wrong answer"
        assert result.is_correct is False
        assert result.submitted_at is not None

    def test_submit_answer_not_found(self, answer_service, answer_repo_mock):
        # 설정
        answer_repo_mock.get_by_id.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            answer_service.submit_answer(
                answer_id="nonexistent_answer_id",
                answer_text="test answer"
            )
        
        answer_repo_mock.get_by_id.assert_called_once_with("nonexistent_answer_id")

    def test_get_answer_by_id(self, answer_service, answer_repo_mock, user_answer):
        # 설정
        answer_repo_mock.get_by_id.return_value = user_answer
        
        # 실행
        result = answer_service.get_answer_by_id(user_answer.id)
        
        # 검증
        answer_repo_mock.get_by_id.assert_called_once_with(user_answer.id)
        assert result == user_answer

    def test_get_answer_by_id_not_found(self, answer_service, answer_repo_mock):
        # 설정
        answer_repo_mock.get_by_id.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            answer_service.get_answer_by_id("nonexistent_answer_id")
        
        answer_repo_mock.get_by_id.assert_called_once_with("nonexistent_answer_id")

    def test_get_answers_by_user_id(self, answer_service, answer_repo_mock, user_answer):
        # 설정
        user_id = "01HUSER12345678ABCDEFGHJK"
        answer_repo_mock.get_by_user_id.return_value = [user_answer]
        
        # 실행
        result = answer_service.get_answers_by_user_id(user_id)
        
        # 검증
        answer_repo_mock.get_by_user_id.assert_called_once_with(user_id)
        assert len(result) == 1
        assert result[0] == user_answer

    def test_get_answers_by_game_id(self, answer_service, answer_repo_mock, user_answer):
        # 설정
        game_id = "01HABCDEFGHJKMNPQRSTUVWXYZ"
        answer_repo_mock.get_by_game_id.return_value = [user_answer]
        
        # 실행
        result = answer_service.get_answers_by_game_id(game_id)
        
        # 검증
        answer_repo_mock.get_by_game_id.assert_called_once_with(game_id)
        assert len(result) == 1
        assert result[0] == user_answer

    def test_get_answer_by_game_and_user(self, answer_service, answer_repo_mock, user_answer):
        # 설정
        game_id = "01HABCDEFGHJKMNPQRSTUVWXYZ"
        user_id = "01HUSER12345678ABCDEFGHJK"
        answer_repo_mock.get_by_game_and_user.return_value = user_answer
        
        # 실행
        result = answer_service.get_answer_by_game_and_user(game_id, user_id)
        
        # 검증
        answer_repo_mock.get_by_game_and_user.assert_called_once_with(game_id, user_id)
        assert result == user_answer

    def test_get_answer_by_game_and_user_not_found(self, answer_service, answer_repo_mock):
        # 설정
        game_id = "01HABCDEFGHJKMNPQRSTUVWXYZ"
        user_id = "01HUSER12345678ABCDEFGHJK"
        answer_repo_mock.get_by_game_and_user.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            answer_service.get_answer_by_game_and_user(game_id, user_id)
        
        answer_repo_mock.get_by_game_and_user.assert_called_once_with(game_id, user_id)

    def test_calculate_score(self, answer_service, answer_repo_mock, game_repo_mock, user_answer, active_game):
        # 설정
        correct_answer = Answer(
            id="01HANSWER1234567890ABCDEFG",
            game_id="01HABCDEFGHJKMNPQRSTUVWXYZ",
            user_id="01HUSER12345678ABCDEFGHJK",
            answer="test answer",
            is_correct=True,
            score=None,  # 점수가 아직 계산되지 않음
            submitted_at=datetime.now() - timedelta(seconds=10),
            created_at=datetime.now() - timedelta(minutes=5)
        )
        
        game_repo_mock.get_by_id.return_value = active_game
        answer_repo_mock.get_by_id.return_value = correct_answer
        
        # 실행
        result = answer_service.calculate_score(correct_answer.id)
        
        # 검증
        answer_repo_mock.get_by_id.assert_called_once_with(correct_answer.id)
        game_repo_mock.get_by_id.assert_called_once_with(active_game.id)
        answer_repo_mock.save.assert_called_once()
        
        assert result.score is not None
        assert result.score > 0  # 정답이므로 점수가 있어야 함

    def test_calculate_score_incorrect_answer(self, answer_service, answer_repo_mock, game_repo_mock, active_game):
        # 설정
        incorrect_answer = Answer(
            id="01HANSWER1234567890ABCDEFG",
            game_id="01HABCDEFGHJKMNPQRSTUVWXYZ",
            user_id="01HUSER12345678ABCDEFGHJK",
            answer="wrong answer",
            is_correct=False,
            score=None,  # 점수가 아직 계산되지 않음
            submitted_at=datetime.now() - timedelta(seconds=10),
            created_at=datetime.now() - timedelta(minutes=5)
        )
        
        game_repo_mock.get_by_id.return_value = active_game
        answer_repo_mock.get_by_id.return_value = incorrect_answer
        
        # 실행
        result = answer_service.calculate_score(incorrect_answer.id)
        
        # 검증
        answer_repo_mock.get_by_id.assert_called_once_with(incorrect_answer.id)
        game_repo_mock.get_by_id.assert_called_once_with(active_game.id)
        answer_repo_mock.save.assert_called_once()
        
        assert result.score == 0  # 오답이므로 점수가 0이어야 함

    def test_calculate_score_answer_not_found(self, answer_service, answer_repo_mock):
        # 설정
        answer_repo_mock.get_by_id.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            answer_service.calculate_score("nonexistent_answer_id")
        
        answer_repo_mock.get_by_id.assert_called_once_with("nonexistent_answer_id")

    def test_calculate_score_no_submission(self, answer_service, answer_repo_mock):
        # 설정
        answer_without_submission = Answer(
            id="01HANSWER1234567890ABCDEFG",
            game_id="01HABCDEFGHJKMNPQRSTUVWXYZ",
            user_id="01HUSER12345678ABCDEFGHJK",
            answer=None,  # 제출되지 않은 답변
            is_correct=None,
            score=None,
            submitted_at=None,
            created_at=datetime.now() - timedelta(minutes=5)
        )
        
        answer_repo_mock.get_by_id.return_value = answer_without_submission
        
        # 실행 및 검증
        with pytest.raises(Exception):
            answer_service.calculate_score(answer_without_submission.id)
        
        answer_repo_mock.get_by_id.assert_called_once_with(answer_without_submission.id)
