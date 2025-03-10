from answer.domain.answer import Answer as AnswerDomain
from answer.domain.answer import AnswerStatus
from answer.domain.repository.answer_repo import IAnswerRepository
from answer.infra.db_models.answer import Answer as AnswerModel

from database import SessionLocal


class AnswerRepository(IAnswerRepository):
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
            status=model.status,
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
            status=domain.status,
        )

    def save(self, answer: AnswerDomain) -> AnswerDomain:
        model = self._to_model(answer)
        with SessionLocal() as db:
            db.add(model)
            db.commit()
            db.refresh(model)
            return self._to_domain(model)

    def update(self, answer: AnswerDomain) -> AnswerDomain:
        with SessionLocal() as db:
            model = db.query(AnswerModel).filter(AnswerModel.id == answer.id).first()
            if not model:
                raise ValueError(f"Answer with id {answer.id} not found")

            model.answer = answer.answer
            model.is_correct = answer.is_correct
            model.solved_at = answer.solved_at
            model.updated_at = answer.updated_at
            model.point = answer.point
            model.status = answer.status

            db.commit()
            db.refresh(model)
            return self._to_domain(model)

    def find_by_id(self, id: str) -> AnswerDomain:
        with SessionLocal() as db:
            model = db.query(AnswerModel).filter(AnswerModel.id == id).first()
            if not model:
                raise ValueError(f"Answer not found with id: {id}")
            return self._to_domain(model)

    def find_by_game_id(self, game_id: str) -> list[AnswerDomain]:
        with SessionLocal() as db:
            models = db.query(AnswerModel).filter(AnswerModel.game_id == game_id).all()
            return [self._to_domain(model) for model in models]

    def find_by_user_id(self, user_id: str) -> list[AnswerDomain]:
        with SessionLocal() as db:
            models = db.query(AnswerModel).filter(AnswerModel.user_id == user_id).all()
            return [self._to_domain(model) for model in models]

    def find_corrected_by_game_id(self, game_id: str) -> list[AnswerDomain]:
        try:
            with SessionLocal() as db:
                models = (
                    db.query(AnswerModel)
                    .filter(
                        AnswerModel.game_id == game_id,
                        AnswerModel.is_correct == True,
                        AnswerModel.solved_at != None,
                        AnswerModel.status == AnswerStatus.SUBMITTED,
                    )
                    .order_by(AnswerModel.solved_at)
                    .all()
                )
            return [self._to_domain(model) for model in models]

        except Exception as e:
            raise e

    def find_unused_by_game_id_and_user_id(
        self, game_id: str, user_id: str
    ) -> list[AnswerDomain] | AnswerDomain:
        with SessionLocal() as db:
            models = (
                db.query(AnswerModel)
                .filter(
                    AnswerModel.game_id == game_id,
                    AnswerModel.user_id == user_id,
                    AnswerModel.status == AnswerStatus.NOT_USED,
                )
                .all()
            )
            return [self._to_domain(model) for model in models] if models else None

    def find_corrected_by_game_id_and_user_id(
        self, game_id: str, user_id: str
    ) -> AnswerDomain:
        with SessionLocal() as db:
            model = (
                db.query(AnswerModel)
                .filter(
                    AnswerModel.game_id == game_id,
                    AnswerModel.user_id == user_id,
                    AnswerModel.is_correct == True,
                )
                .first()
            )
            if not model:
                return None
            return self._to_domain(model)

    def find_not_used_by_game_id_and_user_id(
        self, game_id: str, user_id: str
    ) -> AnswerDomain:
        with SessionLocal() as db:
            model = (
                db.query(AnswerModel)
                .filter(
                    AnswerModel.game_id == game_id,
                    AnswerModel.user_id == user_id,
                    AnswerModel.is_correct == False,
                )
                .first()
            )
            if not model:
                return None
            return self._to_domain(model)

    def delete_by_id(self, id: str) -> None:
        with SessionLocal() as db:
            model = db.query(AnswerModel).filter(AnswerModel.id == id).first()
            if not model:
                raise ValueError(f"Answer not found with id: {id}")
            db.delete(model)
            db.commit()
