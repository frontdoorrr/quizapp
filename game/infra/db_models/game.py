from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Enum
from sqlalchemy.orm import Mapped

from database import Base
from game.domain.game import GameStatus


class Game(Base):
    __tablename__ = "game"

    id: Mapped[str] = Column(String(36), primary_key=True)
    number: Mapped[int] = Column(
        Integer, primary_key=False, autoincrement=True, unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)
    modified_at: Mapped[datetime] = Column(DateTime, nullable=False)
    opened_at: Mapped[datetime] = Column(DateTime, nullable=True)
    closed_at: Mapped[datetime] = Column(DateTime, nullable=True)
    title: Mapped[str] = Column(String(32), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    status: Mapped[GameStatus] = Column(
        Enum(GameStatus), nullable=False, default=GameStatus.DRAFT
    )
    memo: Mapped[str] = Column(Text, nullable=True)
    question: Mapped[str] = Column(Text, nullable=False)
    answer: Mapped[str] = Column(Text, nullable=False)
    question_link: Mapped[str] = Column(String(256), nullable=True)
    answer_link: Mapped[str] = Column(String(256), nullable=True)
