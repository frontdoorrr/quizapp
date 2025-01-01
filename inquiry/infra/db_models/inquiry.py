from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import Mapped, relationship

from database import Base

from inquiry.domain.inquiry import Inquiry


class Inquiry(Base):
    __tablename__ = "inquiry"

    id: Mapped[str] = Column(String(36), primary_key=True)
    name: Mapped[str] = Column(String(32), nullable=False)
    email: Mapped[str] = Column(String(32), nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)
    is_replied: Mapped[bool] = Column(DateTime, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)