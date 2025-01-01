from abc import ABCMeta, abstractmethod
from inquiry.domain.inquiry import Inquiry


class IInquiryRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, inquiry: Inquiry):
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[Inquiry]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> Inquiry:
        raise NotImplementedError

    @abstractmethod
    def update(self, inquiry: Inquiry) -> Inquiry:
        raise NotImplementedError

    @abstractmethod
    def delete(self, inquiry: Inquiry) -> Inquiry:
        raise NotImplementedError
