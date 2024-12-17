from fastapi import HTTPException, status

from database import SessionLocal
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.user import User


class UserRepository(IUserRepository):
    def save(self, user: UserVO):
        db_user = User(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            role=user.role,
            birth=user.birth,
            address=user.address,
            phone=user.phone,
            nickname=user.nickname,
            created_at=user.created_at,
            updated_at=user.updated_at,
            memo=user.memo,
        )
        with SessionLocal() as db:
            db.add(db_user)
            db.commit()

    def find_by_email(self, email: str) -> UserVO:
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return UserVO(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                role=user.role,
                birth=user.birth,
                address=user.address,
                phone=user.phone,
                nickname=user.nickname,
                created_at=user.created_at,
                updated_at=user.updated_at,
                memo=user.memo,
            )

    def find_by_id(self, id: str) -> UserVO:
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return UserVO(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                role=user.role,
                birth=user.birth,
                address=user.address,
                phone=user.phone,
                nickname=user.nickname,
                created_at=user.created_at,
                updated_at=user.updated_at,
                memo=user.memo,
            )

    def find_all(self) -> list[UserVO]:
        with SessionLocal() as db:
            users = db.query(User).all()
            return [
                UserVO(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    password=user.password,
                    role=user.role,
                    birth=user.birth,
                    address=user.address,
                    phone=user.phone,
                    nickname=user.nickname,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    memo=user.memo,
                )
                for user in users
            ]

    def update(self, user_vo: UserVO):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_vo.id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

            user.name = user_vo.name
            user.email = user_vo.email
            user.password = user_vo.password
            user.role = user_vo.role
            user.birth = user_vo.birth
            user.address = user_vo.address
            user.phone = user_vo.phone
            user.nickname = user_vo.nickname
            user.updated_at = user_vo.updated_at
            user.memo = user_vo.memo

            db.commit()
            return user_vo
