import pytest
from datetime import datetime
from answer.application.answer_service import AnswerService
from answer.domain.answer import Answer, AnswerStatus
from game.domain.game import Game


class TestAnswerService:
    @pytest.fixture
    def answer_service(self, mocker):
        self.answer_repo = mocker.Mock()
        self.game_repo = mocker.Mock()
        self.user_repo = mocker.Mock()
        return AnswerService(
            answer_repo=self.answer_repo,
            game_repo=self.game_repo,
            user_repo=self.user_repo,
        )

    def test_submit_answer_correct(self, answer_service):
        # Given
        game_id = "test-game-id"
        user_id = "test-user-id"
        answer_text = "correct answer"

        mock_game = Game(
            id=game_id,
            title="Test Game",
            answer="correct answer",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.game_repo.find_by_id.return_value = mock_game

        mock_answer = Answer(
            id="test-answer-id",
            game_id=game_id,
            user_id=user_id,
            answer="",
            is_correct=False,
            status=AnswerStatus.NOT_USED,
        )
        self.answer_repo.find_not_used_by_game_id_and_user_id.return_value = mock_answer

        # When
        result = answer_service.submit_answer(game_id, user_id, answer_text)

        # Then
        assert result.is_correct == True
        assert result.status == AnswerStatus.SUBMITTED

    def test_get_user_answers(self, answer_service):
        # Given
        user_id = "test-user-id"
        mock_answers = [
            Answer(
                id="answer-1",
                game_id="game-1",
                user_id=user_id,
                answer="test answer 1",
                is_correct=True,
                status=AnswerStatus.SUBMITTED,
            ),
            Answer(
                id="answer-2",
                game_id="game-2",
                user_id=user_id,
                answer="test answer 2",
                is_correct=False,
                status=AnswerStatus.SUBMITTED,
            ),
        ]
        self.answer_repo.find_by_user_id.return_value = mock_answers

        # When
        answers = answer_service.get_answers_by_user(user_id)

        # Then
        assert len(answers) == 2
        assert all(answer.user_id == user_id for answer in answers)
