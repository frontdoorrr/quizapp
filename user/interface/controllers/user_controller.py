from typing import Annotated
from datetime import datetime, date

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from dependency_injector.wiring import inject, Provide

from containers import Container
from user.application.user_service import UserService
from common.auth import CurrentUser, get_current_user, get_admin_user, Role


router = APIRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)
    role: Role = Field(default=Role.USER)
    birth: date
    address: str | None = Field(max_length=32, default=None)
    phone: str = Field(max_length=32)
    nickname: str = Field(min_length=2, max_length=32)


class UpdateUserBody(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)
    birth: date | None = None
    address: str | None = Field(max_length=32, default=None)
    phone: str | None = Field(max_length=32, default=None)
    nickname: str | None = Field(min_length=2, max_length=32, default=None)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: Role
    birth: date
    address: str | None
    phone: str
    nickname: str
    created_at: datetime
    updated_at: datetime
    memo: str | None


class GetUserResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
def create_user(
    user: CreateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    created_user = user_service.create_user(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role,
        birth=user.birth,
        address=user.address,
        phone=user.phone,
        nickname=user.nickname,
    )
    return created_user


@router.put("/{user_id}")
@inject
def update_user(
    user_id: str,
    user: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    user = user_service.update_user(
        user_id=user_id,
        name=user.name,
        password=user.password,
        birth=user.birth,
        address=user.address,
        phone=user.phone,
        nickname=user.nickname,
    )
    return user


@router.get("")
@inject
def get_users(
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_admin_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUserResponse:
    users = user_service.get_users()
    return {
        "users": users,
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    # TODO : 다른 유저를 삭제할 수 없도록 Token에서 유저 아이디를 구한다.
    user_service.delete_user(current_user.id)


@router.post("/login")
@inject
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    access_token = user_service.login(
        email=form_data.username,
        password=form_data.password,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.put("", response_model=UserResponse)
@inject
def update_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = user_service.update_user(
        user_id=current_user.id,
        name=body.name,
        password=body.password,
        birth=body.birth,
        address=body.address,
        phone=body.phone,
        nickname=body.nickname,
    )
    return user
