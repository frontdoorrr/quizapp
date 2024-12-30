from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Text, Date, Enum, Integer
from sqlalchemy.orm import Mapped, relationship

from database import Base
from common.auth import Role


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = Column(String(36), primary_key=True)
    name: Mapped[str] = Column(String(32), nullable=False)
    email: Mapped[str] = Column(String(32), nullable=False, unique=True)
    password: Mapped[str] = Column(String(256), nullable=False)
    role: Mapped[Role] = Column(Enum(Role), nullable=False, default=Role.USER)
    birth: Mapped[date] = Column(Date, nullable=False)
    address: Mapped[str] = Column(String(256), nullable=True)
    phone: Mapped[str] = Column(String(32), nullable=False)
    nickname: Mapped[str] = Column(String(32), nullable=False)
    memo: Mapped[str] = Column(Text, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime, nullable=False)
    last_login_at: Mapped[datetime] = Column(DateTime, nullable=True)

    # Relationships
    answers = relationship("Answer", back_populates="user")


class UserPoint(Base):
    __tablename__ = "user_point"

    user_id: Mapped[str] = Column(String(36), primary_key=True)
    point: Mapped[int] = Column(Integer, nullable=False)


class LoginHistory(Base):
    __tablename__ = "login_history"

    id: Mapped[str] = Column(String(36), primary_key=True)
    user_id: Mapped[str] = Column(String(36), nullable=False)
    login_at: Mapped[datetime] = Column(DateTime, nullable=False)
