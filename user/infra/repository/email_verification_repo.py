"""Email verification repository implementation"""

from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import and_

from database import SessionLocal
from user.domain.repository.email_verification_repo import IEmailVerificationRepository
from user.domain.email_verification import EmailVerification as EmailVerificationVO
from user.infra.db_models.email_verification import EmailVerification


class EmailVerificationRepository(IEmailVerificationRepository):
    """Email verification repository implementation"""

    def save(self, verification: EmailVerificationVO) -> EmailVerificationVO:
        """Save email verification"""
        with SessionLocal() as db:
            db_verification = EmailVerification(
                id=verification.id,
                user_id=verification.user_id,
                token=verification.token,
                verified=verification.verified,
                created_at=verification.created_at,
                verified_at=verification.verified_at,
                expires_at=verification.expires_at,
            )
            db.add(db_verification)
            db.commit()
            db.refresh(db_verification)
            return self._to_vo(db_verification)

    def find_by_token(self, token: str) -> EmailVerificationVO:
        """Find email verification by token"""
        with SessionLocal() as db:
            verification = db.query(EmailVerification).filter(
                and_(
                    EmailVerification.token == token,
                    EmailVerification.verified == False,
                    EmailVerification.expires_at > datetime.now(),
                )
            ).first()
            if not verification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Verification not found or expired",
                )
            return self._to_vo(verification)

    def find_by_user_id(self, user_id: str) -> list[EmailVerificationVO]:
        """Find email verifications by user ID"""
        with SessionLocal() as db:
            verifications = db.query(EmailVerification).filter(
                EmailVerification.user_id == user_id
            ).all()
            return [self._to_vo(v) for v in verifications]

    def update(self, verification: EmailVerificationVO) -> EmailVerificationVO:
        """Update email verification"""
        with SessionLocal() as db:
            db_verification = db.query(EmailVerification).filter(
                EmailVerification.id == verification.id
            ).first()
            if not db_verification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Verification not found",
                )
            db_verification.verified = verification.verified
            db_verification.verified_at = verification.verified_at
            db.commit()
            db.refresh(db_verification)
            return self._to_vo(db_verification)

    def _to_vo(self, verification: EmailVerification) -> EmailVerificationVO:
        """Convert DB model to domain model"""
        return EmailVerificationVO(
            id=verification.id,
            user_id=verification.user_id,
            token=verification.token,
            verified=verification.verified,
            created_at=verification.created_at,
            verified_at=verification.verified_at,
            expires_at=verification.expires_at,
        )
