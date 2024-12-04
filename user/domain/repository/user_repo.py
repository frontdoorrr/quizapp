from abc import ABCMeta, abstractmethod
from user.domain.user import User


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, user: User):
        raise NotImplementedError  # 인터페이스 함수의 구현부는 NotImplementedError를 일으켜서 구현이 필요함을 기술한다.

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
    def update(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str):
        raise NotImplementedError
