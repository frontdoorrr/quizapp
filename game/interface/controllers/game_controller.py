from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from dependency_injector.wiring import inject, Provide
from datetime import datetime

from containers import Container
from game.application.game_service import GameService
from common.auth import get_current_user

router = APIRouter(prefix="/game", tags=["game"])


class CreateGameBody(BaseModel):
    title: str = Field(min_length=2, max_length=32)
    number: int = Field(gt=0)
    description: str = Field(max_length=64)
    question: str = Field(max_length=64)
    answer: str = Field(max_length=64)
    question_link: str = Field(max_length=128)
    answer_link: str = Field(max_length=128)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_game(
    body: CreateGameBody,
    game_service: GameService = Depends(Provide[Container.game_service]),
):

    game = game_service.create_game(
        title=body.title,
        number=body.number,
        description=body.description,
        question=body.question,
        answer=body.answer,
        question_link=body.question_link,
        answer_link=body.answer_link,
    )

    return GameResponse(
        id=game.id,
        number=game.number,
        created_at=game.created_at,
        modified_at=game.modified_at,
        opened_at=game.opened_at,
        closed_at=game.closed_at,
        title=game.title,
        description=game.description,
        status=game.status,
        memo=game.memo,
        question=game.question,
        answer=game.answer,
        question_link=game.question_link,
        answer_link=game.answer_link,
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
    number: int
    created_at: datetime
    modified_at: datetime
    opened_at: datetime | None
    closed_at: datetime | None
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
    opened_at: datetime | None
    closed_at: datetime | None
    title: str
    description: str
    status: str
    memo: str | None
    question: str
    answer: str
    question_link: str | None
    answer_link: str | None
