from typing import Annotated
from ulid import ULID
from datetime import datetime
from user.domain.user import User

from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException, Depends, status
from containers import Container


from common.auth import create_access_token
from utils.crypto import Crypto
from user.domain.repository.user_repo import IUserRepository
from user.infra.repository.user_repo import UserRepository


class UserService:
    @inject
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        self.ulid = ULID()
        self.crypto = Crypto()

    def create_user(
        self,
        name: str,
        email: str,
        password: str,
        memo: str | None = None,
    ):
        _user = None

        try:
            _user = self.user_repo.find_by_email(email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(status_code=422)

        now = datetime.now()
        user: User = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
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
    ):
        user = self.user_repo.find_by_id(user_id)

        if name:
            user.name = name
        if password:
            user.password = self.crtypto.encrypt(password)
        user.updated_at = datetime.now()
        self.user_repo.update(user)
        return user

    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        users = self.user_repo.get_users(page, items_per_page)
        return users

    def delete_user(self, user_id: str):
        return self.user_repo.delete(user_id)

    def login(self, email: str, password: str):
        user = self.user_repo.find_by_email(email=email)

        if not self.crypto.verify(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(payload={"user_id": user.id})
        return access_token
