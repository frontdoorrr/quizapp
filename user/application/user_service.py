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
from config import get_settings

from user.domain.user import User
import os
import re
import uuid
from datetime import datetime, timedelta
from utils.password import is_valid_password, InvalidPasswordFormatError


class UserService:
    @inject
    def __init__(
        self, user_repo: IUserRepository, login_history_repo: ILoginHistoryRepository
    ):
        self.user_repo = user_repo
        self.login_history_repo = login_history_repo
        self.redis_settings = RedisSettings()
        self.crypto = Crypto()
        self.email_sender = EmailSender()
        self.redis = RedisClient(self.redis_settings)
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
        token = secrets.token_urlsafe(8)

        # Save verification token in Redis
        if self.redis.get(key=email):
            self.redis.delete(key=email)
        self.redis.set(
            email,
            token,
            ttl=self.redis_settings.EMAIL_VERIFICATION_TTL,
        )

        # Send verification email
        try:
            self.email_sender.send_verification_email(email, token)
        except Exception as e:
            # 이메일 전송 실패시 토큰 삭제
            self.redis.delete(f"{email}:{token}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def verify_token(self, email: str, token: str) -> None:
        """Verify token

        Args:
            redis key = email
            redis value = token

        Raises:
            HTTPException: If token is invalid or expired
        """
        cached_token = self.redis.get(key=email)
        if not cached_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        # 토큰 검증 성공 시 삭제
        self.redis.delete(key=email)

        # 해당 이메일로 가입된 유저가 있다면 이메일 인증 상태 업데이트
        if token == cached_token:
            return True

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

    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
        new_password2: str,
    ) -> None:
        """사용자 비밀번호 변경

        Args:
            user_id: 사용자 ID
            current_password: 현재 비밀번호
            new_password: 새 비밀번호

        Raises:
            InvalidPasswordError: 현재 비밀번호가 일치하지 않는 경우
            InvalidPasswordFormatError: 새 비밀번호가 유효하지 않은 경우
        """
        user = self.user_repo.find_by_id(user_id)
        if not self.crypto.verify(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="현재 비밀번호가 일치하지 않습니다",
            )

        if new_password != new_password2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호가 일치하지 않습니다",
            )

        hashed_password = self.crypto.encrypt(new_password)
        user.password = hashed_password
        self.user_repo.update(user)

    def request_password_reset(self, email: str) -> None:
        """비밀번호 재설정 요청

        Args:
            email: 사용자 이메일

        Raises:
            HTTPException: 사용자가 존재하지 않는 경우
        """
        try:
            user = self.user_repo.find_by_email(email)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # 임시 토큰 생성
        token = self.ulid.generate()

        # Redis에 토큰 저장 (30분 만료)
        key = f"password_reset:{email}"
        self.redis.set(key, token, ttl=1800)

        # 이메일 발송
        settings = get_settings()
        # 프로토콜을 포함한 완전한 URL 형식으로 변경
        frontend_url = settings.FRONTEND_URL
        if not frontend_url.startswith(('http://', 'https://')):
            frontend_url = f"http://{frontend_url}"
        
        reset_link = f"{frontend_url}/reset-password?email={email}&token={token}"

        # HTML 형식의 이메일 내용 생성
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>비밀번호 재설정</title>
            <style>
                body {{
                    font-family: 'CGF Locust Resistance', 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f9f9f9;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 1px solid #eee;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #d8c27c;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                h1 {{
                    color: #333;
                    font-size: 22px;
                    margin-top: 0;
                }}
                p {{
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #d8c27c;
                    color: white;
                    text-decoration: none;
                    padding: 12px 25px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background-color: #3A5FEF;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #999;
                }}
                .note {{
                    font-size: 13px;
                    color: #888;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Genius Game</div>
                </div>
                <div class="content">
                    <h1>비밀번호 재설정 요청</h1>
                    <p>안녕하세요,</p>
                    <p>귀하의 계정에 대한 비밀번호 재설정 요청이 접수되었습니다. 아래 버튼을 클릭하여 비밀번호를 재설정하세요.</p>
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">비밀번호 재설정</a>
                    </div>
                    <p class="note">* 이 링크는 30분 동안 유효합니다. 만약 비밀번호 재설정을 요청하지 않으셨다면, 이 이메일을 무시하셔도 됩니다.</p>
                    <p>버튼이 작동하지 않는 경우, 아래 링크를 브라우저에 복사하여 붙여넣으세요:</p>
                    <p style="word-break: break-all; font-size: 13px; color: #666;">{reset_link}</p>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} Genius Game. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        self.email_sender.send_email(
            to_email=email,
            subject="비밀번호 재설정",
            content=html_content,
            is_html=True,
        )

    def verify_password_reset_token(self, email: str, token: str) -> bool:
        """비밀번호 재설정 토큰 검증

        Args:
            email: 사용자 이메일
            token: 비밀번호 재설정 토큰

        Returns:
            bool: 토큰이 유효한 경우 True, 그렇지 않은 경우 False
        """
        # 토큰 검증
        key = f"password_reset:{email}"
        stored_token = self.redis.get(key)

        # 디버깅을 위한 로그 추가
        print(f"Verify - Stored token: {stored_token}, Provided token: {token}")

        return stored_token is not None and stored_token == token

    def reset_password(
        self, email: str, token: str, new_password: str, new_password2: str
    ) -> None:
        """비밀번호 재설정

        Args:
            email: 사용자 이메일
            token: 비밀번호 재설정 토큰
            new_password: 새 비밀번호
            new_password2: 새 비밀번호 확인

        Raises:
            HTTPException: 토큰이 유효하지 않거나 만료된 경우
            InvalidPasswordFormatError: 새 비밀번호가 유효하지 않은 경우
        """
        # 토큰 검증
        if not self.verify_password_reset_token(email, token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        # 비밀번호 유효성 검사
        if new_password != new_password2:
            raise InvalidPasswordFormatError("Passwords do not match")

        if not is_valid_password(new_password):
            raise InvalidPasswordFormatError("Invalid password format")

        # 비밀번호 업데이트
        user = self.user_repo.find_by_email(email)
        user.password = self.crypto.encrypt(new_password)
        self.user_repo.update(user)

        # 토큰 삭제
        key = f"password_reset:{email}"
        self.redis.delete(key)
