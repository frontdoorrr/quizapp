"""user service"""

from typing import Annotated
from ulid import ULID
from datetime import datetime, date, timedelta
import secrets
from fastapi import HTTPException, status

from dependency_injector.wiring import inject

from common.auth import Role, create_access_token
from user.infra.db_models.user import LoginHistory
from utils.crypto import Crypto
from utils.email import EmailSender
from user.domain.repository.user_repo import IUserRepository, ILoginHistoryRepository
from common.redis.client import RedisClient
from common.redis.config import RedisSettings

from user.domain.user import User


class UserService:
    @inject
    def __init__(
        self, user_repo: IUserRepository, login_history_repo: ILoginHistoryRepository
    ):
        self.user_repo = user_repo
        self.login_history_repo = login_history_repo
        self.settings = RedisSettings()
        self.crypto = Crypto()
        self.email_sender = EmailSender()
        self.redis = RedisClient(self.settings)
        self.ulid = ULID()

    def create_user(
        self,
        name: str,
        email: str,
        password: str,
        role: Role = Role.USER,
        birth: date | None = None,
        address: str | None = None,
        phone: str | None = None,
        nickname: str | None = None,
        memo: str | None = None,
        coin: int = 0,
    ) -> User:
        _user = None

        try:
            _user = self.user_repo.find_by_email(email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email already exists",
            )

        now = datetime.now()
        user = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
            role=role,
            birth=birth,
            address=address,
            phone=phone,
            nickname=nickname,
            created_at=now,
            updated_at=now,
            memo=memo,
            point=0,  # 초기 포인트는 0으로 설정
            coin=coin,
        )
        self.user_repo.save(user)
        return user

    def update_user(
        self,
        user_id: str,
        name: str | None = None,
        password: str | None = None,
        birth: date | None = None,
        address: str | None = None,
        phone: str | None = None,
        nickname: str | None = None,
    ) -> User:
        user = self.user_repo.find_by_id(user_id)
        if name:
            user.name = name
        if password:
            user.password = self.crypto.encrypt(password)
        if birth:
            user.birth = birth
        if address is not None:
            user.address = address
        if phone:
            user.phone = phone
        if nickname:
            user.nickname = nickname
        user.modified_at = datetime.now()
        self.user_repo.update(user)
        return user

    def get_users(
        self,
        nickname: str | None = None,
        min_point: int | None = None,
        max_point: int | None = None,
        order_by: str | None = None,
        order: str | None = "asc",
    ):
        return self.user_repo.get_users(
            nickname=nickname,
            min_point=min_point,
            max_point=max_point,
            order_by=order_by,
            order=order,
        )

    def get_user_by_id(self, user_id: str) -> User:
        return self.user_repo.find_by_id(user_id)

    def check_nickname_exists(self, nickname: str) -> bool:
        """Check if a nickname already exists

        Args:
            nickname (str): Nickname to check

        Returns:
            bool: True if nickname exists, False otherwise
        """
        try:
            self.user_repo.find_by_nickname(nickname)
            return True
        except HTTPException as e:
            if e.status_code == 404:
                return False
            raise e

    def check_email_exists(self, email: str) -> bool:
        """Check if an email already exists

        Args:
            email (str): Email to check

        Returns:
            bool: True if email exists, False otherwise
        """
        try:
            self.user_repo.find_by_email(email)
            return True
        except HTTPException as e:
            if e.status_code == 422:  # User not found
                return False
            raise e

    def send_verification_email(self, email: str) -> None:
        """Send verification email to the given email address

        Args:
            email (str): Email address to send verification to
        """
        # Generate verification token
        token = secrets.token_urlsafe(32)

        # Save verification token in Redis
        self.redis.set(
            f"email_verify:{token}",
            {"email": email},
            ttl=self.settings.EMAIL_VERIFICATION_TTL,
        )

        # Send verification email
        try:
            self.email_sender.send_verification_email(email, token)
        except Exception as e:
            # 이메일 전송 실패시 토큰 삭제
            self.redis.delete(f"email_verify:{token}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def verify_email(self, token: str) -> None:
        """Verify email with the given token

        Args:
            token (str): Verification token

        Raises:
            HTTPException: If token is invalid or expired
        """
        verification_data = self.redis.get(f"email_verify:{token}")
        if not verification_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        # 토큰 검증 성공 시 삭제
        self.redis.delete(f"email_verify:{token}")

        # 해당 이메일로 가입된 유저가 있다면 이메일 인증 상태 업데이트
        email = verification_data["email"]
        user = self.user_repo.find_by_email(email)
        if user:
            user.email_verified = True
            self.user_repo.update(user)

    def login(self, email: str, password: str) -> dict:
        try:
            user = self.user_repo.find_by_email(email)
            if not self.crypto.verify(password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(
            payload={
                "sub": user.id,
                "email": user.email,
            },
            role=user.role,
        )
        if access_token:
            login_history = LoginHistory(
                id=self.ulid.generate(),
                user_id=user.id,
                login_at=datetime.now(),
            )
            self.login_history_repo.save(login_history)

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
