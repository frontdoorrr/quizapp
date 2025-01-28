"""Email verification model"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, relationship

from database import Base


class EmailVerification(Base):
    """Email verification model"""

    __tablename__ = "email_verification"

    id: Mapped[str] = Column(String(32), primary_key=True)
    user_id: Mapped[str] = Column(String(32), ForeignKey("user.id"))
    token: Mapped[str] = Column(String(64), nullable=False, unique=True)
    verified: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False)
    verified_at: Mapped[datetime] = Column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="email_verifications")
