from fastapi import HTTPException, status

from game.domain.repository.game_repo import IGameRepository
from game.domain.game import Game as GameVO
from game.infra.db_models.game import Game
from game.infra.db import SessionLocal


class GameRepository(IGameRepository):
    def save(self, game: GameVO):
        db_game = Game(
            id=game.id,
            created_at=game.created_at,
            modified_at=game.modified_at,
            opened_at=game.opened_at,
            closed_at=game.closed_at,
            title=game.title,
            description=game.description,
            status=game.status,
            memo=game.memo,
            question=game.question,
            answer=game.answer,
            question_link=game.question_link,
            answer_link=game.answer_link,
        )
        with SessionLocal() as db:
            db.add(db_game)
            db.commit()

    def find_all(self) -> list[GameVO]:
        with SessionLocal() as db:
            games = db.query(Game).all()
            return [
                GameVO(
                    id=game.id,
                    created_at=game.created_at,
                    modified_at=game.modified_at,
                    opened_at=game.opened_at,
                    closed_at=game.closed_at,
                    title=game.title,
                    description=game.description,
                    status=game.status,
                    memo=game.memo,
                    question=game.question,
                    answer=game.answer,
                    question_link=game.question_link,
                    answer_link=game.answer_link,
                )
                for game in games
            ]

    def find_by_id(self, id: str) -> GameVO:
        with SessionLocal() as db:
            game_db = db.query(Game).filter(Game.id == id).first()
            if not game_db:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return GameVO(
                id=game_db.id,
                created_at=game_db.created_at,
                modified_at=game_db.modified_at,
                opened_at=game_db.opened_at,
                closed_at=game_db.closed_at,
                title=game_db.title,
                description=game_db.description,
                status=game_db.status,
                memo=game_db.memo,
                question=game_db.question,
                answer=game_db.answer,
                question_link=game_db.question_link,
                answer_link=game_db.answer_link,
            )

    def update(self, game_vo: GameVO):
        with SessionLocal() as db:
            game = db.query(Game).filter(Game.id == game_vo.id).first()
            if not game:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

            game.id = game_vo.id
            game.created_at = game_vo.created_at
            game.modified_at = game_vo.modified_at
            game.opened_at = game_vo.opened_at
            game.closed_at = game_vo.closed_at
            game.title = game_vo.title
            game.description = game_vo.description
            game.status = game_vo.status
            game.memo = game_vo.memo
            game.question = game_vo.question
            game.answer = game_vo.answer
            game.question_link = game_vo.question_link
            game.answer_link = game_vo.answer_link

            db.commit()
            return game_vo

    def delete(self, game: GameVO):
        raise NotImplementedError

    def find_by_number(self, number):
        raise NotImplementedError

    def find_by_status(self, status):
        raise NotImplementedError
