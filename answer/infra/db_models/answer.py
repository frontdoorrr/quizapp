from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.orm import Mapped, relationship

from database import Base

from answer.domain.answer import AnswerStatus


class Answer(Base):
    __tablename__ = "answer"  # DB 테이블 이름은 소문자

    id: Mapped[str] = Column(String(36), primary_key=True)
    game_id: Mapped[str] = Column(String(36), ForeignKey("game.id"), nullable=False)
    user_id: Mapped[str] = Column(String(36), ForeignKey("user.id"), nullable=False)
    answer: Mapped[str] = Column(Text, nullable=False)
    is_correct: Mapped[bool] = Column(Boolean, nullable=False)
    solved_at: Mapped[datetime] = Column(DateTime, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime, nullable=False)
    point: Mapped[int] = Column(Integer, nullable=False)
    status: Mapped[AnswerStatus] = Column(
        Enum(AnswerStatus), nullable=False, default=AnswerStatus.NOT_USED
    )


# Late binding: relationship을 클래스 정의 후에 설정
from game.infra.db_models.game import Game
from user.infra.db_models.user import User

Answer.game = relationship("Game", back_populates="answers")
Answer.user = relationship("User", back_populates="answers")
