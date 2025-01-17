from datetime import datetime
from sqlalchemy.orm import Session

from answer.domain.answer import Answer as AnswerDomain
from answer.domain.repository.answer_repo import IAnswerRepository
from answer.infra.db_models.answer import Answer as AnswerModel
from database import SessionLocal


class AnswerRepository(IAnswerRepository):
    def __init__(self):
        self.db: Session = SessionLocal()

    def _to_domain(self, model: AnswerModel) -> AnswerDomain:
        return AnswerDomain(
            id=model.id,
            game_id=model.game_id,
            user_id=model.user_id,
            answer=model.answer,
            is_correct=model.is_correct,
            solved_at=model.solved_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            point=model.point,
        )

    def _to_model(self, domain: AnswerDomain) -> AnswerModel:
        return AnswerModel(
            id=domain.id,
            game_id=domain.game_id,
            user_id=domain.user_id,
            answer=domain.answer,
            is_correct=domain.is_correct,
            solved_at=domain.solved_at,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            point=domain.point,
        )

    def save(self, answer: AnswerDomain) -> AnswerDomain:
        model = self._to_model(answer)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_id(self, id: str) -> AnswerDomain:
        model = self.db.query(AnswerModel).filter(AnswerModel.id == id).first()
        if not model:
            raise ValueError(f"Answer not found with id: {id}")
        return self._to_domain(model)

    def find_by_game_id(self, game_id: str) -> list[AnswerDomain]:
        models = self.db.query(AnswerModel).filter(AnswerModel.game_id == game_id).all()
        return [self._to_domain(model) for model in models]

    def find_by_user_id(self, user_id: str) -> list[AnswerDomain]:
        models = self.db.query(AnswerModel).filter(AnswerModel.user_id == user_id).all()
        return [self._to_domain(model) for model in models]

    def find_by_game_id_and_user_id(self, game_id: str, user_id: str) -> AnswerDomain:
        model = (
            self.db.query(AnswerModel)
            .filter(AnswerModel.game_id == game_id, AnswerModel.user_id == user_id)
            .first()
        )
        if not model:
            raise ValueError(f"Answer not found with game_id: {game_id} and user_id: {user_id}")
        return self._to_domain(model)
