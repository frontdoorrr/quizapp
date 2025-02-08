from abc import ABC, abstractmethod
from typing import List, Optional

from user.domain.user import CoinWallet, Coin


class ICoinWalletRepository(ABC):
    @abstractmethod
    def create(self, wallet: CoinWallet) -> CoinWallet:
        pass

    @abstractmethod
    def find_by_id(self, wallet_id: str) -> Optional[CoinWallet]:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[CoinWallet]:
        pass

    @abstractmethod
    def update(self, wallet: CoinWallet) -> CoinWallet:
        pass


class ICoinRepository(ABC):
    @abstractmethod
    def create(self, coin: Coin) -> Coin:
        pass

    @abstractmethod
    def find_by_id(self, coin_id: str) -> Optional[Coin]:
        pass

    @abstractmethod
    def find_by_wallet_id(self, wallet_id: str) -> List[Coin]:
        pass

    @abstractmethod
    def update(self, coin: Coin) -> Coin:
        pass
