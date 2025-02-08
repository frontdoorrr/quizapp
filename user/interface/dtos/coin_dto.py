from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from user.domain.user import CoinStatus


class CoinResponse(BaseModel):
    id: str
    wallet_id: str
    status: CoinStatus
    created_at: datetime
    updated_at: datetime
    memo: Optional[str] = None


class WalletResponse(BaseModel):
    id: str
    user_id: str
    balance: int = Field(ge=0)
    max_balance: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    coins: List[CoinResponse]


class AddCoinRequest(BaseModel):
    memo: Optional[str] = None


class UpdateCoinRequest(BaseModel):
    status: CoinStatus
    memo: Optional[str] = None
