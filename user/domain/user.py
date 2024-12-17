from dataclasses import dataclass
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
    created_at: datetime
    updated_at: datetime
    memo: str | None = None
