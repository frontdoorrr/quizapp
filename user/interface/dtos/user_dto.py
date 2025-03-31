from pydantic import BaseModel, Field, validator, EmailStr
import re
from datetime import date

from user.domain.user import Role
from dataclasses import dataclass


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
    nickname: str | None = None
    email: EmailStr | None = None


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


class ChangePasswordDTO(BaseModel):
    current_password: str = Field(min_length=8, max_length=32)
    new_password: str = Field(min_length=8, max_length=32)
    new_password2: str = Field(min_length=8, max_length=32)

    @validator("new_password")
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

    @validator("new_password2")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("새 비밀번호가 일치하지 않습니다")
        return v


class PasswordResetRequestDTO(BaseModel):
    """비밀번호 재설정 요청 DTO"""

    email: str


class PasswordResetDTO(BaseModel):
    """비밀번호 재설정 DTO"""

    email: str
    token: str
    new_password: str
    new_password2: str


class PasswordResetVerifyDTO(BaseModel):
    """비밀번호 재설정 토큰 검증 DTO"""

    email: str
    token: str
