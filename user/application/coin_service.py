from datetime import datetime
from uuid import uuid4
from typing import List, Optional

from user.domain.repository.coin_repo import ICoinWalletRepository, ICoinRepository
from user.domain.user import CoinWallet, Coin, CoinStatus
from user.domain.exceptions import (
    WalletNotFoundError,
    UserWalletNotFoundError,
    InsufficientCoinsError,
    MaxBalanceExceededError,
)


class CoinService:
    def __init__(
        self, wallet_repository: ICoinWalletRepository, coin_repository: ICoinRepository
    ):
        self.wallet_repo = wallet_repository
        self.coin_repo = coin_repository

    def create_wallet(self, user_id: str, max_balance: int = 5) -> CoinWallet:
        """사용자의 코인 지갑을 생성합니다."""
        # 이미 지갑이 있는지 확인
        existing_wallet = self.wallet_repo.find_by_user_id(user_id)
        if existing_wallet:
            return existing_wallet

        # 새 지갑 생성
        now = datetime.utcnow()
        wallet = CoinWallet(
            id=str(uuid4()),
            user_id=user_id,
            balance=0,
            max_balance=max_balance,
            created_at=now,
            updated_at=now,
        )
        return self.wallet_repo.create(wallet)

    def get_wallet(self, user_id: str) -> CoinWallet:
        """사용자의 코인 지갑을 조회합니다."""
        wallet = self.wallet_repo.find_by_user_id(user_id)
        if not wallet:
            raise UserWalletNotFoundError(user_id)
        return wallet

    def add_coin(self, user_id: str, memo: Optional[str] = None) -> Coin:
        """사용자의 지갑에 코인을 추가합니다."""
        wallet = self.get_wallet(user_id)

        # 최대 잔액 체크
        if wallet.balance >= wallet.max_balance:
            raise MaxBalanceExceededError(wallet.id, wallet.max_balance)

        # 코인 생성
        now = datetime.utcnow()
        coin = Coin(
            id=str(uuid4()),
            wallet_id=wallet.id,
            created_at=now,
            updated_at=now,
            status=CoinStatus.ACTIVE,
            memo=memo,
        )
        created_coin = self.coin_repo.create(coin)

        # 지갑 잔액 업데이트
        wallet.balance += 1
        wallet.updated_at = now
        self.wallet_repo.update(wallet)

        return created_coin

    def use_coin(self, user_id: str, memo: Optional[str] = None) -> Coin:
        """사용자의 지갑에서 코인을 사용합니다."""
        wallet = self.get_wallet(user_id)

        # 잔액 체크
        if wallet.balance < 1:
            raise InsufficientCoinsError(wallet.id, 1, wallet.balance)

        # 사용 가능한 코인 찾기
        coins = self.coin_repo.find_by_wallet_id(wallet.id)
        active_coin = next(
            (coin for coin in coins if coin.status == CoinStatus.ACTIVE), None
        )
        if not active_coin:
            raise InsufficientCoinsError(wallet.id, 1, 0)

        # 코인 상태 업데이트
        now = datetime.utcnow()
        active_coin.status = CoinStatus.USED
        active_coin.updated_at = now
        active_coin.memo = memo
        updated_coin = self.coin_repo.update(active_coin)

        # 지갑 잔액 업데이트
        wallet.balance -= 1
        wallet.updated_at = now
        self.wallet_repo.update(wallet)

        return updated_coin

    def get_coins(self, user_id: str) -> List[Coin]:
        """사용자의 모든 코인을 조회합니다."""
        wallet = self.get_wallet(user_id)
        return self.coin_repository.find_by_wallet_id(wallet.id)

    def get_active_coins(self, user_id: str) -> List[Coin]:
        """사용자의 사용 가능한 코인을 조회합니다."""
        all_coins = self.get_coins(user_id)
        return [coin for coin in all_coins if coin.status == CoinStatus.ACTIVE]
