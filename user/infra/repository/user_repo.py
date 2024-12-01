from fastapi import HTTPException

from database import SessionLocal
from utils.db_utils import row_to_dict

from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.user import User


class UserRepository(IUserRepository):
    def save(self, user: UserVO):
        new_user = User(
            id=user.id,
            email=user.email,
            name=user.name,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at,
            memo=user.memo,
        )

        with SessionLocal() as db:
            try:
                db = SessionLocal()
                db.add(new_user)
                db.commit()
            finally:
                db.close()

    def find_by_email(self, email: str) -> UserVO:
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=422)

        return UserVO(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at,
            memo=user.memo,
        )

    def find_by_id(self, id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=422)
        return UserVO(**row_to_dict(user))

    def update(self, user_vo: UserVO):
        with SessionLocal() as db:
            user = db.qeury(User).filter(User.id == user_vo.id).first()
            if not user:
                raise HTTPException(status_code=422)
            user.name = user_vo.name
            user.password = user_vo.password
            db.add(user)
            db.commit()
        return user

    def get_users(self) -> list[UserVO]:
        with SessionLocal() as db:
            users = db.query(User).all()
        return [UserVO(**row_to_dict(user)) for user in users]
