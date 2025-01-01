from typing import Annotated
from datetime import datetime, date

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from dependency_injector.wiring import inject, Provide

from containers import Container
from user.application.user_service import UserService
from common.auth import CurrentUser, get_current_user, get_admin_user, Role


router = APIRouter(prefix="/user", tags=["user"])


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)
    role: Role = Field(default=Role.USER)
    birth: date = Field(...)  # 명시적으로 필수 필드로 지정
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
    point: int


class GetUsersRequest(BaseModel):
    nickname: str | None = None
    min_point: int | None = None
    max_point: int | None = None
    order_by: str | None = None  # 'point' or 'nickname'
    order: str | None = "asc"  # 'asc' or 'desc'


class GetUserResponse(BaseModel):
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
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
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


@router.get("", response_model=GetUserResponse)
@inject
async def get_users(
    request: GetUsersRequest = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUserResponse:
    users = user_service.get_users(
        nickname=request.nickname,
        min_point=request.min_point,
        max_point=request.max_point,
        order_by=request.order_by,
        order=request.order,
    )
    return GetUserResponse(
        users=[
            UserResponse(
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
) -> UserResponse:

    return user_service.get_user_by_id(current_user.id)


@router.post("/login")
@inject
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service]),
):

    print(form_data.username)
    print(form_data.password)

    return user_service.login(email=form_data.username, password=form_data.password)


@router.put("/me")
@inject
def update_my_info(
    body: UpdateUserBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
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
