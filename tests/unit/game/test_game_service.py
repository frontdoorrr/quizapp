import pytest
from datetime import datetime
from game.application.game_service import GameService
from game.domain.game import Game, GameStatus, GameDifficulty


class TestGameService:
    @pytest.fixture
    def game_service(self, mocker):
        self.game_repo = mocker.Mock()
        return GameService(game_repo=self.game_repo)

    def test_create_game(self, game_service):
        # Given
        game_data = {
            "title": "Test Game",
            "description": "Test Description",
            "difficulty": GameDifficulty.EASY,
            "answer": "test answer",
            "hint": "test hint",
            "max_players": 100,
        }

        # When
        game = game_service.create_game(**game_data)

        # Then
        assert game.title == game_data["title"]
        assert game.difficulty == game_data["difficulty"]
        assert game.status == GameStatus.ACTIVE

    def test_get_active_games(self, game_service):
        # Given
        mock_games = [
            Game(
                id="test-game-1",
                title="Game 1",
                description="Description 1",
                difficulty=GameDifficulty.EASY,
                status=GameStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Game(
                id="test-game-2",
                title="Game 2",
                description="Description 2",
                difficulty=GameDifficulty.MEDIUM,
                status=GameStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        self.game_repo.find_active_games.return_value = mock_games

        # When
        games = game_service.get_active_games()

        # Then
        assert len(games) == 2
        assert all(game.status == GameStatus.ACTIVE for game in games)

    def test_end_game(self, game_service):
        # Given
        game_id = "test-game-id"
        mock_game = Game(
            id=game_id,
            title="Test Game",
            status=GameStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.game_repo.find_by_id.return_value = mock_game

        # When
        game = game_service.end_game(game_id)

        # Then
        assert game.status == GameStatus.ENDED
