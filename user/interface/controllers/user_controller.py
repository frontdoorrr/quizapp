from typing import Annotated
import logging

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide

from containers import Container
from user.application.user_service import UserService
from user.application.coin_service import CoinService
from user.interface.dtos.user_dto import (
    UserRequestDTO,
    UserResponseDTO,
    UserCreateDTO,
    UserUpdateDTO,
    TokenVerificationDTO,
    EmailVerficationDTO,
)
from common.auth import CurrentUser, get_current_user

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/user", tags=["user"])


class UserResponseListDTO(BaseModel):
    users: list[UserResponseDTO]


@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
def create_user(
    user: UserCreateDTO,
    user_service: UserService = Depends(Provide[Container.user_service]),
    coin_service: CoinService = Depends(Provide[Container.coin_service]),
) -> UserResponseDTO:
    logger.debug(f"Received user data: {user.dict()}")

    created_user = user_service.create_user(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role,
        birth=user.birth,
        address=user.address,
        phone=user.phone,
        nickname=user.nickname,
        coin=0,
    )

    coin_service.create_wallet(created_user.id, max_balance=20)
    return created_user


@router.put("/{user_id}")
@inject
def update_user(
    user_id: str,
    user: UserUpdateDTO,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponseDTO:
    updated_user = user_service.update_user(
        user_id=user_id,
        name=user.name,
        password=user.password,
        birth=user.birth,
        address=user.address,
        phone=user.phone,
        nickname=user.nickname,
    )
    return updated_user


@router.get("", response_model=UserResponseListDTO)
@inject
async def get_users(
    request: UserRequestDTO = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponseListDTO:
    users = user_service.get_users(
        nickname=request.nickname,
        min_point=request.min_point,
        max_point=request.max_point,
        order_by=request.order_by,
        order=request.order,
    )
    return UserResponseListDTO(
        users=[
            UserResponseDTO(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                birth=user.birth,
                address=user.address,
                phone=user.phone,
                nickname=user.nickname,
                created_at=user.created_at,
                updated_at=user.updated_at,
                memo=user.memo,
                point=user.point,
            )
            for user in users
        ]
    )


@router.get("/me")
@inject
def get_my_info(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponseDTO:

    return user_service.get_user_by_id(current_user.id)


@router.post("/login")
@inject
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service]),
):

    return user_service.login(email=form_data.username, password=form_data.password)


@router.put("/me")
@inject
def update_my_info(
    body: UserUpdateDTO,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponseDTO:
    updated_user = user_service.update_user(
        user_id=current_user.id,
        name=body.name,
        password=body.password,
        birth=body.birth,
        address=body.address,
        phone=body.phone,
        nickname=body.nickname,
    )
    return updated_user


@router.patch("/me", response_model=UserResponseDTO)
@inject
async def update_me(
    request: UserUpdateDTO,
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponseDTO:
    updated_user = user_service.update_user(
        user_id=current_user.id,
        name=request.name,
        nickname=request.nickname,
        phone=request.phone,
        address=request.address,
    )
    return UserResponseDTO(
        id=updated_user.id,
        name=updated_user.name,
        email=updated_user.email,
        role=updated_user.role,
        birth=updated_user.birth,
        address=updated_user.address,
        phone=updated_user.phone,
        nickname=updated_user.nickname,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        memo=updated_user.memo,
        point=updated_user.point,
    )


@router.get("/check-nickname/{nickname}")
@inject
async def check_nickname(
    nickname: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Check if a nickname is available
    """
    exists = user_service.check_nickname_exists(nickname)
    return {"exists": exists}


@router.get("/check-email/{email}")
@inject
async def check_email(
    email: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Check if an email is available
    """
    try:
        exists = user_service.check_email_exists(email)
        return {"exists": exists}
    except Exception as e:
        logger.error(f"Error checking email availability: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/send-verification-email")
@inject
async def send_verification_email(
    body: EmailVerficationDTO,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """
    Send verification email to current user
    """

    try:
        user_service.send_verification_email(body.email)
        logger.debug(f"Verification email sent successfully")
        return {"message": "Verification email sent"}
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/verify-token")
@inject
def verify_token(
    body: TokenVerificationDTO,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """Verify email with token

    Args:
        token (str): Verification token
        user_service (UserService): User service instance
    """
    try:
        user_service.verify_token(email=body.email, token=body.token)
        return {"message": "Email verified successfully"}
    except Exception as e:
        logger.error(f"Failed to verify email: {str(e)}")
        raise e
