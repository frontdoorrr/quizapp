from dataclasses import dataclass
import dataclasses
from datetime import datetime, date
from common.auth import Role
from enum import Enum


class CoinStatus(str, Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    INACTIVE = "INACTIVE"


@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    role: Role
    birth: date
    address: str | None
    phone: str
    nickname: str
    point: int
    coin: int
    created_at: datetime
    updated_at: datetime
    memo: str | None = None
    email_verified: bool = False


@dataclass
class LoginHistory:
    id: str
    user_id: str
    created_at: datetime


@dataclass
class CoinWallet:
    id: str
    user_id: str
    balance: int
    max_balance: int  # 최대 coin 잔액 / default: 5
    created_at: datetime
    updated_at: datetime


@dataclass
class Coin:
    id: str
    wallet_id: str
    created_at: datetime
    updated_at: datetime
    status: CoinStatus = CoinStatus.ACTIVE
    memo: str | None = None
