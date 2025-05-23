from typing import Annotated
import logging

from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.exceptions import RequestValidationError
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
    ChangePasswordDTO,
    PasswordResetRequestDTO,
    PasswordResetDTO,
    PasswordResetVerifyDTO,
    UserRankResponseDTO,
    UserRankResponseListDTO,
)
from common.auth import CurrentUser, get_admin_user, get_current_user

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
    current_user: CurrentUser = Depends(get_admin_user), # 어드민만 조회가능하도록 수정
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponseListDTO:
    users = user_service.get_users(
        nickname=request.nickname,
        min_point=request.min_point,
        max_point=request.max_point,
        order_by=request.order_by,
        order=request.order,
        offset=request.offset,
        limit=request.limit,
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

@router.get("/ranked", response_model=UserRankResponseListDTO)
@inject
async def get_ranked_users(
    request: UserRequestDTO = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserRankResponseListDTO:
    try:
        users = user_service.get_users(
            nickname=request.nickname,
            min_point=request.min_point,
            max_point=request.max_point,
            order_by=request.order_by,
            order=request.order,
            offset=request.offset,
            limit=request.limit,
        )
        return UserRankResponseListDTO(
            users=[
                UserRankResponseDTO(
                    nickname=user.nickname,
                    point=user.point,
                )
                for user in users
            ]
        )
    except Exception as e:
        logger.error(f"Error getting ranked users: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me")
@inject
def get_my_info(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponseDTO:

    return user_service.get_user_by_id(current_user.id)


@router.get("/{user_id}")
@inject
def get_user_by_id(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
    current_user: CurrentUser = Depends(get_admin_user),
) -> UserResponseDTO:
    return user_service.get_user_by_id(user_id)


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
        if user_service.verify_token(email=body.email, token=body.token):
            return {"message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
            )
    except Exception as e:
        logger.error(f"Failed to verify email: {str(e)}")
        raise e


# @router.post("/change-password")
# @inject
# async def change_password(
#     request: ChangePasswordDTO,
#     current_user: CurrentUser = Depends(get_current_user),
#     user_service: UserService = Depends(Provide[Container.user_service]),
# ) -> None:
#     """비밀번호 변경 API

#     Args:
#         request: 비밀번호 변경 요청 DTO
#         current_user: 현재 로그인한 사용자
#         user_service: 사용자 서비스
#     """
#     try:
#         user_service.change_password(
#             user_id=current_user.id,
#             current_password=request.current_password,
#             new_password=request.new_password,
#             new_password2=request.new_password2,
#         )
#         return Response(status_code=status.HTTP_200_OK)
#     except ValueError as e:
#         logger.error(f"비밀번호 변경 유효성 검사 실패: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
#     except Exception as e:
#         logger.error(f"비밀번호 변경 실패: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="비밀번호 변경 중 오류가 발생했습니다",
#         )


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
@inject
def request_password_reset(
    request: PasswordResetRequestDTO,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """비밀번호 재설정 요청"""
    user_service.request_password_reset(request.email)
    return {"message": "Password reset email sent"}


@router.post("/password-reset", status_code=status.HTTP_200_OK)
@inject
def reset_password(
    request: PasswordResetDTO,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """비밀번호 재설정"""
    user_service.reset_password(
        request.email,
        request.token,
        request.new_password,
        request.new_password2,
    )
    return {"message": "Password reset successful"}


@router.post("/password-reset/verify", status_code=status.HTTP_200_OK)
@inject
def verify_password_reset_token(
    request: PasswordResetVerifyDTO,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    """비밀번호 재설정 토큰 검증"""
    is_valid = user_service.verify_password_reset_token(request.email, request.token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    return {"message": "Token is valid"}
