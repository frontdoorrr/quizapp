from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, relationship

from database import Base
from game.infra.db_models.game import Game
from user.infra.db_models.user import User


class Answer(Base):
    __tablename__ = "answer"

    id: Mapped[str] = Column(String(36), primary_key=True)
    game_id: Mapped[str] = Column(String(36), ForeignKey("game.id"), nullable=False)
    user_id: Mapped[str] = Column(String(36), ForeignKey("user.id"), nullable=False)
    answer: Mapped[str] = Column(Text, nullable=False)
    is_correct: Mapped[bool] = Column(Boolean, nullable=False)
    solved_at: Mapped[datetime] = Column(DateTime, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime, nullable=False)
    point: Mapped[int] = Column(Integer, nullable=False)

    # Relationships
    game: Mapped[Game] = relationship("Game", back_populates="answers")
    user: Mapped[User] = relationship("User", back_populates="answers")
