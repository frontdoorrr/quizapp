from dependency_injector.wiring import inject

from game.domain.repository.game_repo import IGameRepository
from datetime import datetime
from game.domain.game import Game


class GameService:
    @inject
    def __init__(self, game_repo: IGameRepository):
        self.game_repo = game_repo

    def create_game(
        self,
        number: int,
        title: str,
        description: str,
        status: str = "Outstanding",
        memo: str | None = None,
        question: str = None,
        answer: str = None,
        question_link: str | None = None,
        answer_link: str | None = None,
    ) -> Game:
        _game = None

        try:
            _game = self.game_repo.find_by_number(number)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _game:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Number already exists",
            )

        now = datetime.now()
        game = Game(
            id=self.ulid.generate(),
            number=number,
            created_at=now,
            modified_at=now,
            opened_at=now,
            closed_at=now,
            title=title,
            description=description,
            status=status,
            memo=memo,
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
