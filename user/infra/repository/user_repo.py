from fastapi import HTTPException, status

from database import SessionLocal
from user.domain.repository.user_repo import IUserRepository, ILoginHistoryRepository
from user.domain.user import User as UserVO
from user.domain.user import LoginHistory as LoginHistoryVO
from user.infra.db_models.user import User, LoginHistory


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
                point=user.point,
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
                point=user.point,
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
                    point=user.point,
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


class LoginHistoryRepository(ILoginHistoryRepository):
    def save(self, login_history: LoginHistoryVO):
        login_history = LoginHistory(
            id=login_history.id,
            user_id=login_history.user_id,
            login_at=login_history.login_at,
        )
        with SessionLocal() as db:
            db.add(login_history)
            db.commit()  # DB에 저장

    def find_by_user_id(self, user_id: str) -> list[LoginHistoryVO]:
        with SessionLocal() as db:
            login_histories = (
                db.query(LoginHistory).filter(LoginHistory.user_id == user_id).all()
            )
            return [
                LoginHistoryVO(
                    id=login_history.id,
                    user_id=login_history.user_id,
                    login_at=login_history.login_at,
                )
                for login_history in login_histories
            ]

    def delete(self, login_history: LoginHistoryVO):
        with SessionLocal() as db:
            login_history = (
                db.query(LoginHistory)
                .filter(LoginHistory.id == login_history.id)
                .first()
            )
            db.delete(login_history)
            db.commit()  # DB에서 삭제

        return login_history

    def find_all(self) -> list[LoginHistoryVO]:
        with SessionLocal() as db:
            login_histories = db.query(LoginHistory).all()
            return [
                LoginHistoryVO(
                    id=login_history.id,
                    user_id=login_history.user_id,
                    login_at=login_history.login_at,
                )
                for login_history in login_histories
            ]

    def update(self, login_history: LoginHistoryVO):
        with SessionLocal() as db:
            login_history = (
                db.query(LoginHistory)
                .filter(LoginHistory.id == login_history.id)
                .first()
            )
            login_history.user_id = login_history.user_id
            login_history.login_at = login_history.login_at

            db.commit()
            return login_history
