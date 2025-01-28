from dataclasses import dataclass
import dataclasses
from datetime import datetime, date
from common.auth import Role


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
