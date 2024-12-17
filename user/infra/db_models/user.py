from datetime import datetime
from sqlalchemy import String, DateTime, Text, Column
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from common.auth import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = Column(String(36), primary_key=True)
    name: Mapped[str] = Column(String(32), nullable=False)
    email: Mapped[str] = Column(String(64), nullable=False, unique=True)
    password: Mapped[str] = Column(String(64), nullable=False)
    role: Mapped[str] = Column(String(32), nullable=False, default=Role.USER)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime, nullable=False)
    memo: Mapped[str] = Column(Text, nullable=True)
