from abc import ABC, abstractmethod
from user.domain.user import User, LoginHistory


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_id(self, id: str) -> User:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User:
        """
        Search User by Email.
        If there is not user, 422 Error occurs.
        """
        pass

    @abstractmethod
    def find_by_nickname(self, nickname: str) -> User:
        pass

    @abstractmethod
    def find_all(self) -> list[User]:
        pass


class ILoginHistoryRepository(ABC):
    @abstractmethod
    def save(self, login_history: LoginHistory) -> LoginHistory:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[LoginHistory]:
        pass

    @abstractmethod
    def find_all(self) -> list[LoginHistory]:
        pass

    @abstractmethod
    def update(self, login_history: LoginHistory) -> LoginHistory:
        pass

    @abstractmethod
    def delete(self, login_history: LoginHistory) -> LoginHistory:
        pass
