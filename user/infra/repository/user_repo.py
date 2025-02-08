from fastapi import HTTPException, status
from sqlalchemy import desc
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
            coin=user.coin,
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
                coin=user.coin,
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
                coin=user.coin,
            )

    def find_by_nickname(self, nickname: str) -> UserVO:
        with SessionLocal() as db:
            user = db.query(User).filter(User.nickname == nickname).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return UserVO(
                id=user.id,
                email=user.email,
                password=user.password,
                name=user.name,
                birth=user.birth,
                address=user.address,
                phone=user.phone,
                nickname=user.nickname,
                created_at=user.created_at,
                updated_at=user.updated_at,
                memo=user.memo,
                point=user.point,
                coin=user.coin,
                role=user.role,
            )

    def find_by_verification_token(self, token: str) -> UserVO:
        with SessionLocal() as db:
            user = db.query(User).filter(User.email_verification_token == token).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return UserVO(
                id=user.id,
                email=user.email,
                password=user.password,
                name=user.name,
                birth=user.birth,
                address=user.address,
                phone=user.phone,
                nickname=user.nickname,
                created_at=user.created_at,
                updated_at=user.updated_at,
                memo=user.memo,
                point=user.point,
                coin=user.coin,
                email_verified=user.email_verified,
                email_verification_token=user.email_verification_token,
                email_verification_sent_at=user.email_verification_sent_at,
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
                    coin=user.coin,
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
            user.coin = user_vo.coin

            db.commit()
            return user_vo

    def get_users(
        self,
        nickname: str | None = None,
        min_point: int | None = None,
        max_point: int | None = None,
        order_by: str | None = None,
        order: str | None = "asc",
    ) -> list[UserVO]:
        db = SessionLocal()
        try:
            query = db.query(User)

            # 필터 적용
            if nickname:
                query = query.filter(User.nickname.ilike(f"%{nickname}%"))
            if min_point is not None:
                query = query.filter(User.point >= min_point)
            if max_point is not None:
                query = query.filter(User.point <= max_point)

            # 정렬 적용
            if order_by:
                print(f"Ordering by {order_by} in {order} order")  # 디버그 로그
                order_column = getattr(User, order_by)
                if order == "desc":
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(order_column)

            users = query.all()
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
                    coin=user.coin,
                )
                for user in users
            ]
        finally:
            db.close()


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
