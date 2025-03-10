from pydantic import BaseModel, Field, validator, EmailStr
import re
from datetime import date

from user.domain.user import Role


class UserBase(BaseModel):
    pass


class UserRequestDTO(UserBase):
    nickname: str | None = None
    min_point: int | None = None
    max_point: int | None = None
    order_by: str | None = None  # 'point' or 'nickname'
    order: str | None = "asc"  # 'asc' or 'desc'


class UserCreateDTO(UserBase):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)
    role: Role = Field(default=Role.USER)
    birth: date = Field(...)  # 명시적으로 필수 필드로 지정
    address: str | None = Field(max_length=32, default=None)
    phone: str = Field(max_length=32)
    nickname: str = Field(min_length=2, max_length=32)

    @validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("비밀번호는 최소 1개의 대문자를 포함해야 합니다")
        if not re.search(r"[a-z]", v):
            raise ValueError("비밀번호는 최소 1개의 소문자를 포함해야 합니다")
        if not re.search(r"[0-9]", v):
            raise ValueError("비밀번호는 최소 1개의 숫자를 포함해야 합니다")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("비밀번호는 최소 1개의 특수문자를 포함해야 합니다")
        return v

    @validator("password")
    def validate_password(cls, v):
        if v is None:  # password가 None이면 검증 스킵
            return v
        if not re.search(r"[A-Z]", v):
            raise ValueError("비밀번호는 최소 1개의 대문자를 포함해야 합니다")
        if not re.search(r"[a-z]", v):
            raise ValueError("비밀번호는 최소 1개의 소문자를 포함해야 합니다")
        if not re.search(r"[0-9]", v):
            raise ValueError("비밀번호는 최소 1개의 숫자를 포함해야 합니다")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("비밀번호는 최소 1개의 특수문자를 포함해야 합니다")
        return v


class UserResponseDTO(UserBase):
    id: str
    name: str


class UserResponseListDTO(BaseModel):
    users: list[UserResponseDTO]


class UserUpdateDTO(UserBase):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)
    birth: date | None = None
    address: str | None = Field(max_length=32, default=None)
    phone: str | None = Field(max_length=32, default=None)
    nickname: str | None = Field(min_length=2, max_length=32, default=None)


class EmailVerficationDTO(BaseModel):
    email: EmailStr = Field(max_length=64)


class TokenVerificationDTO(BaseModel):
    token: str = Field(max_length=64)
    email: EmailStr = Field(max_length=64)
