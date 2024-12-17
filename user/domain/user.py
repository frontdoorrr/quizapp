from dataclasses import dataclass
from datetime import datetime
from common.auth import Role


@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    role: Role
    created_at: datetime
    updated_at: datetime
    memo: str | None = None
