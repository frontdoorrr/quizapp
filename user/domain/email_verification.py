"""Email verification domain model"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EmailVerification:
    """Email verification domain model"""
    id: str
    user_id: str
    token: str
    verified: bool
    created_at: datetime
    verified_at: datetime | None
    expires_at: datetime
