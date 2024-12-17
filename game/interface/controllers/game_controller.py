from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from game.application.game_service import GameService
from common.auth import get_current_user

router = APIRouter(prefix="/game")


class CreateGameBody(BaseModel):
    title: str = Field(min_length=2, max_length=32)
    description: str = Field(max_length=64)
    question: str = Field(max_length=64)
    answer: str = Field(max_length=64)
    question_link: str = Field(max_length=128)
    answer_link: str = Field(max_length=128)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_game(
    body: CreateGameBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    return game_service.create_game(
        title=body.title,
        description=body.description,
        question=body.question,
        answer=body.answer,
        question_link=body.question_link,
        answer_link=body.answer_link,
    )


class UpdateGameBody(BaseModel):
    title: str = Field(min_length=2, max_length=32)
    description: str = Field(max_length=64)
    question: str = Field(max_length=64)
    answer: str = Field(max_length=64)
    question_link: str = Field(max_length=128)
    answer_link: str = Field(max_length=128)


@router.put("/{game_id}")
@inject
async def update_game(
    game_id: str,
    body: UpdateGameBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    return game_service.update_game(
        id=game_id,
        title=body.title,
        description=body.description,
        question=body.question,
        answer=body.answer,
        question_link=body.question_link,
        answer_link=body.answer_link,
    )


class GameResponse(BaseModel):
    id: str
    created_at: datetime
    modified_at: datetime
    opened_at: datetime
    closed_at: datetime
    title: str
    description: str
    status: str
    memo: str | None
    question: str
    answer: str
    question_link: str | None
    answer_link: str | None


class GetGameResponse(BaseModel):
    id: str
    created_at: datetime
    modified_at: datetime
    opened_at: datetime
    closed_at: datetime
    title: str
    description: str
    status: str
    memo: str | None
    question: str
    answer: str
    question_link: str | None
    answer_link: str | None
