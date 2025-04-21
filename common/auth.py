from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import get_settings

settings = get_settings()

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


@dataclass
class CurrentUser:
    id: str
    role: Role
    email: str | None = None


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def create_access_token(
    payload: dict, role: Role, expires_delta: timedelta = timedelta(hours=6)
):
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update(
        {
            "role": role.value,
            "exp": expire,
        }
    )
    encoded_jwt = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token=token)

    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id or not role or role not in [Role.USER.value, Role.ADMIN.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return CurrentUser(id=user_id, role=Role(role))


def get_admin_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token=token)

    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id or not role or role != Role.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return CurrentUser(id=user_id, role=Role(role))
