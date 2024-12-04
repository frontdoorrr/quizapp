from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from dependency_injector.wiring import inject, Provide


from containers import Container
from user.application.user_service import UserService

router = APIRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


class GetUserResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]


@router.post("", status_code=201)
@inject
def create_user(
    user: CreateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
    # user_service: Annotated[UserService, Depends(UserService)],
) -> UserResponse:
    user_service = UserService()
    created_user = user_service.create_user(
        name=user.name,
        email=user.email,
        password=user.password,
    )
    return created_user


class UpdateUser(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)


@router.put("/{user_id}")
@inject
def update_user(
    user_id: str,
    user: UpdateUser,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    user = user_service.update_user(
        user_id=user_id,
        name=user.name,
        password=user.password,
    )
    return user


@router.get("")
@inject
def get_users(
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUserResponse:
    users = user_service.get_users()
    return {
        "users": users,
    }


@router.delete("", status_code=204)
@inject
def delete_user(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    # TODO : 다른 유저를 삭제할 수 없도록 Token에서 유저 아이디를 구한다.
    user_service.delete_user(user_id)
