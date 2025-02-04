from abc import ABCMeta, abstractmethod
from game.domain.game import Game


class IGameRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, game: Game):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> Game:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[Game]:
        raise NotImplementedError

    @abstractmethod
    def update(self, game: Game) -> Game:
        raise NotImplementedError

    @abstractmethod
    def find_latest(self) -> Game | None:
        """Find the game with the highest number

        Returns:
            Game | None: The game with the highest number, or None if no games exist
        """
        raise NotImplementedError
