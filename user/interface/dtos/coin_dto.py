from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from user.domain.user import CoinStatus


class CoinBase(BaseModel):
    pass


class WalletBase(BaseModel):
    pass


class CoinResponseDTO(BaseModel):
    id: str
    wallet_id: str
    status: CoinStatus
    created_at: datetime
    updated_at: datetime
    memo: Optional[str] = None


class CoinUpdateDTO(CoinBase):
    status: CoinStatus
    memo: Optional[str] = None


class WalletResponseDTO(BaseModel):
    id: str
    user_id: str
    balance: int = Field(ge=0)
    max_balance: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    coins: List[CoinResponseDTO]


class CoinCreateDTO(CoinBase):
    memo: Optional[str] = None


class CoinUpdateDTO(CoinBase):
    status: CoinStatus
    memo: Optional[str] = None


class CoinResponseListDTO(BaseModel):
    coins: List[CoinResponseDTO]
    total_count: int
