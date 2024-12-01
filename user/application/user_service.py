from typing import Annotated
from ulid import ULID
from datetime import datetime
from user.domain.user import User

from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException, Depends
from containers import Container


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
