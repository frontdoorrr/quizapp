from abc import ABCMeta, abstractmethod
from answer.domain.answer import Answer


class IAnswerRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, answer: Answer) -> Answer:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> Answer:
        raise NotImplementedError

    @abstractmethod
    def find_by_game_id(self, game_id: str) -> list[Answer]:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[Answer]:
        raise NotImplementedError

    @abstractmethod
    def find_corrected_by_game_id_and_user_id(
        self, game_id: str, user_id: str
    ) -> Answer:
        raise NotImplementedError

    @abstractmethod
    def find_corrected_by_game_id(self, game_id: str) -> list[Answer]:
        raise NotImplementedError

    @abstractmethod
    def find_unused_by_game_id_and_user_id(
        self, game_id: str, user_id: str
    ) -> list[Answer]:
        raise NotImplementedError
