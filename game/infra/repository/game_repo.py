from fastapi import HTTPException, status

from database import SessionLocal
from game.domain.repository.game_repo import IGameRepository
from game.domain.game import Game as GameVO
from game.infra.db_models.game import Game


class GameRepository(IGameRepository):
    def save(self, game: GameVO):
        db_game = Game(
            id=game.id,
            number=game.number,
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
            db.refresh(db_game)
            game.number = db_game.number  # 자동 생성된 number를 도메인 객체에 반영

    def find_all(self) -> list[GameVO]:
        with SessionLocal() as db:
            games = db.query(Game).all()
            return [
                GameVO(
                    id=game.id,
                    number=game.number,
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
            game = db.query(Game).filter(Game.id == id).first()
            if not game:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return GameVO(
                id=game.id,
                number=game.number,
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

    def update(self, game: GameVO) -> GameVO:
        with SessionLocal() as db:
            db_game = db.query(Game).filter(Game.id == game.id).first()
            if not db_game:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            db_game.title = game.title
            db_game.description = game.description
            db_game.status = game.status
            db_game.memo = game.memo
            db_game.question = game.question
            db_game.answer = game.answer
            db_game.question_link = game.question_link
            db_game.answer_link = game.answer_link
            db_game.modified_at = game.modified_at
            db_game.opened_at = game.opened_at
            db_game.closed_at = game.closed_at

            db.commit()
            return game

    def delete(self, game: GameVO):
        raise NotImplementedError

    def find_by_number(self, number):
        raise NotImplementedError

    def find_by_status(self, status):
        raise NotImplementedError
