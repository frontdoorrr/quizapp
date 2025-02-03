from datetime import datetime
from ulid import ULID

from dependency_injector.wiring import inject

from game.domain.game import Game, GameStatus
from game.domain.repository.game_repo import IGameRepository


class GameService:
    @inject
    def __init__(self, game_repo: IGameRepository):
        self.game_repo = game_repo
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
        now = datetime.now()
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

        game.modified_at = datetime.now()

        self.game_repo.update(game)
        return game

    def get_game(self, id: str) -> Game:
        """Get a game by id

        Args:
            id (str): Game id

        Returns:
            Game: Game object
        """
        return self.game_repo.find_by_id(id)

    def get_games(self, status: GameStatus | None = None) -> list[Game]:
        """Get all games with optional status filter

        Args:
            status (GameStatus | None, optional): Game status filter. Defaults to None.

        Returns:
            list[Game]: List of games
        """
        if status:
            return self.game_repo.find_by_status(status)
        return self.game_repo.find_all()
