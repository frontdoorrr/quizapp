from contextlib import nullcontext
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import Mapped

from database import Base


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = Column("id", String, primary_key=True)

    created_at: Mapped[str] = Column("created_at", DateTime, nullable=False)
    modified_at: Mapped[str] = Column("modified_at", DateTime, nullable=False)
    opened_at: Mapped[str] = Column("opened_at", DateTime, nullable=False)
    closed_at: Mapped[str] = Column("closed_at", DateTime, nullable=False)

    title: Mapped[str] = Column("title", String)
    description: Mapped[str] = Column("description", Text, nullable=True)
    status: Mapped[str] = Column("status", String,nullable=False, default="Outstanding"
    memo: Mapped[str] = Column("memo", Text, nullable=True)
    question: Mapped[str] = Column("question", String, nullable=False)
    answer: Mapped[str] = Column("answer", String, nullable=False)
    question_link: Mapped[str] = Column("question_link", String, nullable=True)
    answer_link: Mapped[str] = Column("answer_link", String, nullable)
