from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, Field

from user.application.coin_service import CoinService
from user.domain.user import CoinStatus
from user.interface.dtos.coin_dto import (
    CoinCreateDTO,
    CoinResponseDTO,
    CoinResponseListDTO,
    WalletResponseDTO,
)
from user.domain.exceptions import (
    WalletNotFoundError,
    UserWalletNotFoundError,
    InsufficientCoinsError,
    MaxBalanceExceededError,
)
from containers import Container


router = APIRouter(
    prefix="/user/{user_id}/coin",
    tags=["coins"],
)


@router.get("/wallet", response_model=WalletResponseDTO)
@inject
async def get_wallet(
    user_id: str,
    coin_service: CoinService = Depends(Provide[Container.coin_service]),
) -> WalletResponseDTO:
    """사용자의 코인 지갑 정보를 조회합니다."""
    try:
        wallet = coin_service.get_wallet(user_id)
        coins = coin_service.get_coins(user_id)
        return WalletResponseDTO(
            id=wallet.id,
            user_id=wallet.user_id,
            balance=wallet.balance,
            max_balance=wallet.max_balance,
            created_at=wallet.created_at,
            updated_at=wallet.updated_at,
            coins=[
                CoinResponseDTO(
                    id=coin.id,
                    wallet_id=coin.wallet_id,
                    status=coin.status,
                    created_at=coin.created_at,
                    updated_at=coin.updated_at,
                    memo=coin.memo,
                )
                for coin in coins
            ],
        )
    except UserWalletNotFoundError:
        # 지갑이 없으면 새로 생성
        wallet = coin_service.create_wallet(user_id)
        return WalletResponseDTO(
            id=wallet.id,
            user_id=wallet.user_id,
            balance=wallet.balance,
            max_balance=wallet.max_balance,
            created_at=wallet.created_at,
            updated_at=wallet.updated_at,
            coins=[],
        )


@router.post("", response_model=CoinResponseDTO)
@inject
async def add_coin(
    user_id: str,
    request: CoinCreateDTO,
    coin_service: CoinService = Depends(Provide[Container.coin_service]),
) -> CoinResponseDTO:
    """사용자의 지갑에 코인을 추가합니다."""
    try:
        coin = coin_service.add_coin(user_id, request.memo)
        return CoinResponseDTO(
            id=coin.id,
            wallet_id=coin.wallet_id,
            status=coin.status,
            created_at=coin.created_at,
            updated_at=coin.updated_at,
            memo=coin.memo,
        )
    except MaxBalanceExceededError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Adding coin would exceed maximum balance of {e.max_balance}",
        )
    except UserWalletNotFoundError:
        raise HTTPException(status_code=404, detail="User wallet not found")


@router.post("/use", response_model=CoinResponseDTO)
@inject
async def use_coin(
    user_id: str,
    request: CoinCreateDTO,
    coin_service: CoinService = Depends(Provide[Container.coin_service]),
) -> CoinResponseDTO:
    """사용자의 지갑에서 코인을 사용합니다."""
    try:
        coin = coin_service.use_coin(user_id, request.memo)
        return CoinResponseDTO(
            id=coin.id,
            wallet_id=coin.wallet_id,
            status=coin.status,
            created_at=coin.created_at,
            updated_at=coin.updated_at,
            memo=coin.memo,
        )
    except InsufficientCoinsError:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    except UserWalletNotFoundError:
        raise HTTPException(status_code=404, detail="User wallet not found")


@router.get("/history", response_model=CoinResponseListDTO)
@inject
async def get_coin_history(
    user_id: str,
    status: Optional[CoinStatus] = None,
    coin_service: CoinService = Depends(Provide[Container.coin_service]),
):
    """사용자의 코인 사용/획득 내역을 조회합니다."""
    try:
        wallet = coin_service.get_wallet(user_id)
        if not wallet:
            raise HTTPException(
                status_code=404,
                detail=f"Wallet not found for user {user_id}",
            )

        coins = coin_service.get_coins(user_id)
        if status:
            coins = [coin for coin in coins if coin.status == status]

        return CoinResponseListDTO(
            coins=[
                CoinResponseDTO(
                    id=coin.id,
                    wallet_id=coin.wallet_id,
                    status=coin.status,
                    created_at=coin.created_at,
                    updated_at=coin.updated_at,
                    memo=coin.memo,
                )
                for coin in coins
            ],
            total_count=len(coins),
        )

    except WalletNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet not found for user {user_id}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
