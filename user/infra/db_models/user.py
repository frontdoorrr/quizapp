from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Text, Date
from sqlalchemy.orm import Mapped

from database import Base
from common.auth import Role


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = Column(String(36), primary_key=True)
    name: Mapped[str] = Column(String(32), nullable=False)
    email: Mapped[str] = Column(String(64), nullable=False, unique=True)
    password: Mapped[str] = Column(String(128), nullable=False)
    role: Mapped[str] = Column(String(32), nullable=False, default=Role.USER)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime, nullable=False)
    birth: Mapped[date] = Column(Date, nullable=False)
    address: Mapped[str] = Column(String(32), nullable=True)
    phone: Mapped[str] = Column(String(32), nullable=False)
    nickname: Mapped[str] = Column(String(32), nullable=False)
    memo: Mapped[str] = Column(Text, nullable=True)
