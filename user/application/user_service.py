from typing import Annotated
from ulid import ULID
from datetime import datetime, date

from dependency_injector.wiring import inject
from fastapi import HTTPException, status

from common.auth import Role, create_access_token
from user.infra.db_models.user import LoginHistory
from utils.crypto import Crypto
from user.domain.repository.user_repo import IUserRepository, ILoginHistoryRepository
from user.domain.user import User


class UserService:
    @inject
    def __init__(
        self, user_repo: IUserRepository, login_history_repo: ILoginHistoryRepository
    ):
        self.user_repo = user_repo
        self.login_history_repo = login_history_repo
        self.ulid = ULID()
        self.crypto = Crypto()

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

    def get_users(self, page: int = 1, items_per_page: int = 10) -> dict:
        users = self.user_repo.find_all()
        total_count = len(users)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_users = users[start_idx:end_idx]

        return {
            "total_count": total_count,
            "page": page,
            "users": paginated_users,
        }

    def get_user_by_id(self, user_id: str) -> User:
        return self.user_repo.find_by_id(user_id)

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
