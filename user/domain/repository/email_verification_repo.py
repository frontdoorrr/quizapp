"""Email verification repository interface"""

from abc import ABC, abstractmethod
from user.domain.email_verification import EmailVerification


class IEmailVerificationRepository(ABC):
    """Email verification repository interface"""

    @abstractmethod
    def save(self, verification: EmailVerification) -> EmailVerification:
        """Save email verification"""
        pass

    @abstractmethod
    def find_by_token(self, token: str) -> EmailVerification:
        """Find email verification by token"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[EmailVerification]:
        """Find email verifications by user ID"""
        pass

    @abstractmethod
    def update(self, verification: EmailVerification) -> EmailVerification:
        """Update email verification"""
        pass
