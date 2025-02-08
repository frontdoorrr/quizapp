from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from common.database import session
from user.domain.repository.coin_repo import ICoinWalletRepository, ICoinRepository
from user.domain.user import CoinWallet, Coin, CoinStatus
from user.infra.db_models.user import CoinWallet as CoinWalletModel
from user.infra.db_models.user import Coin as CoinModel


class CoinWalletRepository(ICoinWalletRepository):
    def __init__(self, session: Session = session):
        self.session = session

    def _to_domain(self, model: CoinWalletModel) -> CoinWallet:
        return CoinWallet(
            id=model.id,
            user_id=model.user_id,
            balance=model.balance,
            max_balance=model.max_balance,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, domain: CoinWallet) -> CoinWalletModel:
        return CoinWalletModel(
            id=domain.id,
            user_id=domain.user_id,
            balance=domain.balance,
            max_balance=domain.max_balance,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    def create(self, wallet: CoinWallet) -> CoinWallet:
        model = self._to_model(wallet)
        self.session.add(model)
        self.session.commit()
        return self._to_domain(model)

    def find_by_id(self, wallet_id: str) -> Optional[CoinWallet]:
        stmt = select(CoinWalletModel).where(CoinWalletModel.id == wallet_id)
        result = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(result) if result else None

    def find_by_user_id(self, user_id: str) -> Optional[CoinWallet]:
        stmt = select(CoinWalletModel).where(CoinWalletModel.user_id == user_id)
        result = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(result) if result else None

    def update(self, wallet: CoinWallet) -> CoinWallet:
        model = self._to_model(wallet)
        self.session.merge(model)
        self.session.commit()
        return wallet


class CoinRepository(ICoinRepository):
    def __init__(self, session: Session = session):
        self.session = session

    def _to_domain(self, model: CoinModel) -> Coin:
        return Coin(
            id=model.id,
            wallet_id=model.wallet_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status=model.status,
            memo=model.memo,
        )

    def _to_model(self, domain: Coin) -> CoinModel:
        return CoinModel(
            id=domain.id,
            wallet_id=domain.wallet_id,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            status=domain.status,
            memo=domain.memo,
        )

    def create(self, coin: Coin) -> Coin:
        model = self._to_model(coin)
        self.session.add(model)
        self.session.commit()
        return self._to_domain(model)

    def find_by_id(self, coin_id: str) -> Optional[Coin]:
        stmt = select(CoinModel).where(CoinModel.id == coin_id)
        result = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(result) if result else None

    def find_by_wallet_id(self, wallet_id: str) -> List[Coin]:
        stmt = select(CoinModel).where(CoinModel.wallet_id == wallet_id)
        results = self.session.execute(stmt).scalars().all()
        return [self._to_domain(result) for result in results]

    def update(self, coin: Coin) -> Coin:
        model = self._to_model(coin)
        self.session.merge(model)
        self.session.commit()
        return coin
