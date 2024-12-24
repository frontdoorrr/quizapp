from abc import ABCMeta, abstractmethod
from user.domain.user import User, LoginHistory


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str) -> User:
        """
        Search User by Email.
        If there is not user, 422 Error occurs.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User) -> User:
        raise NotImplementedError


class ILoginHistoryRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, login_history: LoginHistory) -> LoginHistory:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[LoginHistory]:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[LoginHistory]:
        raise NotImplementedError

    @abstractmethod
    def update(self, login_history: LoginHistory) -> LoginHistory:
        raise NotImplementedError

    @abstractmethod
    def delete(self, login_history: LoginHistory) -> LoginHistory:
        raise NotImplementedError
