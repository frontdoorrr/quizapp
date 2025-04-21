import pytest
from datetime import datetime
from game.application.game_service import GameService
from game.domain.game import Game, GameStatus


class TestGameService:
    @pytest.fixture
    def game_service(self, mocker):
        self.game_repo = mocker.Mock()
        self.redis_client = mocker.Mock()
        return GameService(game_repo=self.game_repo, redis_client=self.redis_client)

    def test_create_game(self, game_service):
        # Given
        game_data = {
            "title": "Test Game",
            "number": 1,
            "description": "Test Description",
            "question": "Test Question",
            "answer": "test answer",
            "question_link": "https://example.com/question",
            "answer_link": "https://example.com/answer",
        }

        # When
        game = game_service.create_game(**game_data)

        # Then
        assert game.title == game_data["title"]
        assert game.number == game_data["number"]
        assert game.description == game_data["description"]
        assert game.question == game_data["question"]
        assert game.answer == game_data["answer"]
        assert game.question_link == game_data["question_link"]
        assert game.answer_link == game_data["answer_link"]
        assert game.status == GameStatus.DRAFT
        assert self.game_repo.save.called

    def test_update_game(self, game_service):
        # Given
        game_id = "test-game-id"
        mock_game = Game(
            id=game_id,
            number=1,
            title="Original Title",
            description="Original Description",
            question="Original Question",
            answer="Original Answer",
            question_link="https://example.com/original",
            answer_link="https://example.com/original",
            status=GameStatus.DRAFT,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            opened_at=None,
            closed_at=None,
            memo=None,
        )
        self.game_repo.find_by_id.return_value = mock_game

        # When
        updated_game = game_service.update_game(
            id=game_id,
            title="Updated Title",
            description="Updated Description",
            question="Updated Question",
            answer="Updated Answer",
            question_link="https://example.com/updated",
            answer_link="https://example.com/updated",
        )

        # Then
        assert updated_game.title == "Updated Title"
        assert updated_game.description == "Updated Description"
        assert updated_game.question == "Updated Question"
        assert updated_game.answer == "Updated Answer"
        assert updated_game.question_link == "https://example.com/updated"
        assert updated_game.answer_link == "https://example.com/updated"
        assert self.game_repo.update.called

    def test_get_game(self, game_service):
        # Given
        game_id = "test-game-id"
        mock_game = Game(
            id=game_id,
            number=1,
            title="Test Game",
            description="Test Description",
            status=GameStatus.OPEN,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            opened_at=None,
            closed_at=None,
            question="Test Question",
            answer="Test Answer",
            question_link=None,
            answer_link=None,
            memo=None,
        )
        self.game_repo.find_by_id.return_value = mock_game

        # When
        game = game_service.get_game(game_id)

        # Then
        assert game.id == game_id
        assert game.title == "Test Game"
        self.game_repo.find_by_id.assert_called_once_with(game_id)

    def test_get_game_not_found(self, game_service):
        # Given
        game_id = "non-existent-id"
        self.game_repo.find_by_id.return_value = None

        # When/Then
        with pytest.raises(Exception, match=f"Game {game_id} not found"):
            game_service.get_game(game_id)

    def test_get_OPEN_games(self, game_service):
        # Given
        mock_games = [
            Game(
                id="test-game-1",
                number=1,
                title="Game 1",
                description="Description 1",
                status=GameStatus.OPEN,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                opened_at=datetime.now(),
                closed_at=None,
                question="Question 1",
                answer="Answer 1",
                question_link=None,
                answer_link=None,
                memo=None,
            ),
            Game(
                id="test-game-2",
                number=2,
                title="Game 2",
                description="Description 2",
                status=GameStatus.OPEN,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                opened_at=datetime.now(),
                closed_at=None,
                question="Question 2",
                answer="Answer 2",
                question_link=None,
                answer_link=None,
                memo=None,
            ),
        ]
        self.game_repo.find_by_status.return_value = mock_games

        # When
        games = game_service.get_games(GameStatus.OPEN)

        # Then
        assert len(games) == 2
        assert all(game.status == GameStatus.OPEN for game in games)
        self.game_repo.find_by_status.assert_called_once_with(GameStatus.OPEN)

    def test_get_all_games(self, game_service):
        # Given
        mock_games = [
            Game(
                id="test-game-1",
                number=1,
                title="Game 1",
                description="Description 1",
                status=GameStatus.OPEN,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                opened_at=datetime.now(),
                closed_at=None,
                question="Question 1",
                answer="Answer 1",
                question_link=None,
                answer_link=None,
                memo=None,
            ),
            Game(
                id="test-game-2",
                number=2,
                title="Game 2",
                description="Description 2",
                status=GameStatus.DRAFT,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                opened_at=None,
                closed_at=None,
                question="Question 2",
                answer="Answer 2",
                question_link=None,
                answer_link=None,
                memo=None,
            ),
        ]
        self.game_repo.find_all.return_value = mock_games

        # When
        games = game_service.get_games()

        # Then
        assert len(games) == 2
        self.game_repo.find_all.assert_called_once()

    def test_get_current_game(self, game_service):
        # Given
        mock_game = Game(
            id="latest-game-id",
            number=10,  # 가장 높은 번호
            title="Latest Game",
            description="Latest Description",
            status=GameStatus.OPEN,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            opened_at=datetime.now(),
            closed_at=None,
            question="Latest Question",
            answer="Latest Answer",
            question_link=None,
            answer_link=None,
            memo=None,
        )
        self.game_repo.find_latest.return_value = mock_game

        # When
        game = game_service.get_current_game()

        # Then
        assert game.id == "latest-game-id"
        assert game.title == "Latest Game"
        self.game_repo.find_latest.assert_called_once()

    def test_get_current_game_not_found(self, game_service):
        # Given
        self.game_repo.find_latest.return_value = None

        # When/Then
        with pytest.raises(Exception, match="No games found"):
            game_service.get_current_game()

    def test_close_game(self, game_service):
        # Given
        game_id = "test-game-id"
        mock_game = Game(
            id=game_id,
            number=1,
            title="Test Game",
            status=GameStatus.OPEN,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            opened_at=datetime.now(),
            closed_at=None,
            description="Test Description",
            question="Test Question",
            answer="Test Answer",
            question_link=None,
            answer_link=None,
            memo=None,
        )
        self.game_repo.find_by_id.return_value = mock_game

        # When
        closed_game = game_service.close_game(game_id)

        # Then
        assert closed_game.status == GameStatus.CLOSED
        assert closed_game.closed_at is not None
        self.game_repo.update.assert_called_once()
        self.redis_client.enqueue.assert_called_once_with({"game_id": game_id})

    def test_close_already_closed_game(self, game_service):
        # Given
        game_id = "test-game-id"
        mock_game = Game(
            id=game_id,
            number=1,
            title="Test Game",
            status=GameStatus.CLOSED,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            opened_at=datetime.now(),
            closed_at=datetime.now(),
            description="Test Description",
            question="Test Question",
            answer="Test Answer",
            question_link=None,
            answer_link=None,
            memo=None,
        )
        self.game_repo.find_by_id.return_value = mock_game

        # When/Then
        with pytest.raises(ValueError, match="Game is already closed"):
            game_service.close_game(game_id)

    def test_close_game_not_found(self, game_service):
        # Given
        game_id = "non-existent-id"
        self.game_repo.find_by_id.return_value = None

        # When/Then
        with pytest.raises(ValueError, match=f"Game not found: {game_id}"):
            game_service.close_game(game_id)

    def test_update_game_closing_time(self, game_service):
        # Given
        game_id = "test-game-id"
        mock_game = Game(
            id=game_id,
            number=1,
            title="Test Game",
            status=GameStatus.OPEN,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            opened_at=datetime.now(),
            closed_at=None,
            description="Test Description",
            question="Test Question",
            answer="Test Answer",
            question_link=None,
            answer_link=None,
            memo=None,
        )
        self.game_repo.find_by_id.return_value = mock_game
        closing_time = datetime.now()

        # When
        updated_game = game_service.update_game_closing_time(game_id, closing_time)

        # Then
        assert updated_game.closed_at == closing_time
        self.game_repo.update.assert_called_once()

    def test_update_game_closing_time_not_found(self, game_service):
        # Given
        game_id = "non-existent-id"
        self.game_repo.find_by_id.return_value = None
        closing_time = datetime.now()

        # When/Then
        with pytest.raises(ValueError, match=f"Game not found: {game_id}"):
            game_service.update_game_closing_time(game_id, closing_time)

    @pytest.mark.parametrize(
        "status", [GameStatus.DRAFT, GameStatus.OPEN, GameStatus.CLOSED]
    )
    def test_get_games_by_status_parameterized(self, game_service, status):
        # Given
        mock_games = [
            Game(
                id=f"test-game-{i}",
                number=i,
                title=f"Game {i}",
                description=f"Description {i}",
                status=status,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                opened_at=datetime.now() if status != GameStatus.DRAFT else None,
                closed_at=datetime.now() if status == GameStatus.CLOSED else None,
                question=f"Question {i}",
                answer=f"Answer {i}",
                question_link=None,
                answer_link=None,
                memo=None,
            )
            for i in range(3)
        ]
        self.game_repo.find_by_status.return_value = mock_games

        # When
        games = game_service.get_games(status)

        # Then
        assert len(games) == 3
        assert all(game.status == status for game in games)
        self.game_repo.find_by_status.assert_called_once_with(status)
