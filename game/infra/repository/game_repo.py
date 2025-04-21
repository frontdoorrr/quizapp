from fastapi import HTTPException, status

from database import SessionLocal
from game.domain.repository.game_repo import IGameRepository
from game.domain.game import Game as GameVO
from game.infra.db_models.game import Game, GameStatus


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

    def find_by_id(self, id: str) -> GameVO | None:
        with SessionLocal() as db:
            db_game = db.query(Game).filter(Game.id == id).first()
            if not db_game:
                return None
            return GameVO(
                id=db_game.id,
                number=db_game.number,
                created_at=db_game.created_at,
                modified_at=db_game.modified_at,
                opened_at=db_game.opened_at,
                closed_at=db_game.closed_at,
                title=db_game.title,
                description=db_game.description,
                status=db_game.status,
                memo=db_game.memo,
                question=db_game.question,
                answer=db_game.answer,
                question_link=db_game.question_link,
                answer_link=db_game.answer_link,
            )

    def update(self, game: GameVO) -> GameVO:
        with SessionLocal() as db:
            db_game = db.query(Game).filter(Game.id == game.id).first()
            if not db_game:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game {game.id} not found",
                )

            db_game.title = game.title
            db_game.description = game.description
            db_game.modified_at = game.modified_at
            db_game.opened_at = game.opened_at
            db_game.closed_at = game.closed_at
            db_game.status = game.status
            db_game.memo = game.memo
            db_game.question = game.question
            db_game.answer = game.answer
            db_game.question_link = game.question_link
            db_game.answer_link = game.answer_link

            db.commit()
            db.refresh(db_game)

            return GameVO(
                id=db_game.id,
                number=db_game.number,
                created_at=db_game.created_at,
                modified_at=db_game.modified_at,
                opened_at=db_game.opened_at,
                closed_at=db_game.closed_at,
                title=db_game.title,
                description=db_game.description,
                status=db_game.status,
                memo=db_game.memo,
                question=db_game.question,
                answer=db_game.answer,
                question_link=db_game.question_link,
                answer_link=db_game.answer_link,
            )

    def find_latest(self) -> GameVO | None:
        """Find the game with the highest number using a direct SQL query

        Returns:
            GameVO | None: The game with the highest number, or None if no games exist
        """
        with SessionLocal() as db:
            # TODO
            db_game = (
                db.query(Game)
                .filter(Game.status == GameStatus.OPEN)
                .order_by(Game.number.desc())
                .first()
            )
            if not db_game:
                return None
            return GameVO(
                id=db_game.id,
                number=db_game.number,
                created_at=db_game.created_at,
                modified_at=db_game.modified_at,
                opened_at=db_game.opened_at,
                closed_at=db_game.closed_at,
                title=db_game.title,
                description=db_game.description,
                status=db_game.status,
                memo=db_game.memo,
                question=db_game.question,
                answer=db_game.answer,
                question_link=db_game.question_link,
                answer_link=db_game.answer_link,
            )

    def delete(self, game: GameVO):
        raise NotImplementedError

    def find_by_number(self, number):
        raise NotImplementedError

    def find_by_status(self, status):
        with SessionLocal() as db:
            games = db.query(Game).filter(Game.status == status).all()
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
