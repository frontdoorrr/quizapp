from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from enum import Enum
from fastapi import HTTPException

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


@router.get("/{game_id}", response_model=GameResponse)
@inject
async def get_game(
    game_id: str,
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    """Get a game by id

    Args:
        game_id (str): Game id
        game_service (GameService): Game service

    Returns:
        GameResponse: Game response
    """
    game = game_service.get_game(game_id)
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


@router.get("", response_model=list[GameResponse])
@inject
async def get_games(
    status: str | None = None,
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    """Get all games with optional status filter

    Args:
        status (str | None, optional): Game status filter. Defaults to None.
        game_service (GameService): Game service

    Returns:
        list[GameResponse]: List of games
    """

    game_status = GameStatus(status.upper()) if status else None
    games = game_service.get_games(game_status)
    return [
        GameResponse(
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
        for game in games
    ]


@router.get("/current/", response_model=GameResponse)
@inject
def get_current_game(
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    """Get the most recently created game

    Args:
        game_service (GameService): Game service

    Returns:
        GameResponse: The most recent game response

    Raises:
        HTTPException: 404 if no games found
    """
    try:
        game = game_service.get_current_game()
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
