from abc import ABCMeta, abstractmethod
from user.domain.user import User


class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, user: User):
        raise NotImplementedError  # 인터페이스 함수의 구현부는 NotImplementedError를 일으켜서 구현이 필요함을 기술한다.
