from abc import ABCMeta, abstractmethod  # ABC
from game.domain.game import Game


class IGameRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, game: Game):
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[Game]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> Game:
        raise NotImplementedError

    @abstractmethod
    def update(self, game: Game) -> Game:
        raise NotImplementedError

    @abstractmethod
    def delete(self, game: Game) -> Game:
        raise NotImplementedError
