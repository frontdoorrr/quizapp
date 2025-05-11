from fastapi import APIRouter, Depends, status, HTTPException


from dependency_injector.wiring import inject, Provide
from containers import Container

from game.application.game_service import GameService
from game.domain.game import GameStatus
from game.interface.dtos.game_dtos import GameCreateDTO, GameResponseDTO, GameUpdateDTO, CurrentGameResponseDTO
from common.auth import CurrentUser, get_admin_user

router = APIRouter(prefix="/game", tags=["game"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_game(
    body: GameCreateDTO,
    game_service: GameService = Depends(Provide[Container.game_service]),
    current_user: CurrentUser = Depends(get_admin_user),
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

    return GameResponseDTO(
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
        # answer=game.answer,
        question_link=game.question_link,
        # answer_link=game.answer_link,
    )


@router.put("/{game_id}")
@inject
async def update_game(
    game_id: str,
    body: GameUpdateDTO,
    game_service: GameService = Depends(Provide[Container.game_service]),
    current_user: CurrentUser = Depends(get_admin_user),
):
    return game_service.update_game(
        id=game_id,
        title=body.title,
        description=body.description,
        question=body.question,
        answer=body.answer,
        question_link=body.question_link,
        answer_link=body.answer_link,
        status=body.status,
    )


@router.get("/current/", response_model=CurrentGameResponseDTO)
@inject
def get_current_game(
    game_service: GameService = Depends(Provide[Container.game_service]),
):

    try:
        game = game_service.get_current_game()
        return CurrentGameResponseDTO(
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
            # answer=game.answer,
            question_link=game.question_link,
            # answer_link=game.answer_link,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{game_id}", response_model=GameResponseDTO)
@inject
async def get_game(
    game_id: str,
    current_user: CurrentUser = Depends(get_admin_user),
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    """Get a game by id

    Args:
        game_id (str): Game id
        game_service (GameService): Game service

    Returns:
        GameResponseDTO: Game response
    """
    game = game_service.get_game(game_id)
    return GameResponseDTO(
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


@router.get("", response_model=list[GameResponseDTO])
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
        list[GameResponseDTO]: List of games
    """

    game_status = GameStatus(status.upper()) if status else None
    games = game_service.get_games(game_status)
    return [
        GameResponseDTO(
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
            # answer=game.answer,
            question_link=game.question_link,
            # answer_link=game.answer_link,
        )
        for game in games
    ]


@router.post("/{game_id}/close", response_model=GameResponseDTO)
@inject
async def close_game(
    game_id: str,
    game_service: GameService = Depends(Provide[Container.game_service]),
    current_user: CurrentUser = Depends(get_admin_user),
) -> GameResponseDTO:
    """게임을 종료하고 점수 계산을 시작"""
    game = game_service.close_game(game_id)
    return GameResponseDTO(
        id=game.id,
        number=game.number,
        title=game.title,
        description=game.description,
        status=game.status,
        created_at=game.created_at,
        modified_at=game.modified_at,
        opened_at=game.opened_at,
        closed_at=game.closed_at,
        question=game.question,
        # answer=game.answer if game.status == GameStatus.CLOSED else None,
        question_link=game.question_link,
        # answer_link=game.answer_link if game.status == GameStatus.CLOSED else None,
    )


@router.delete("/{game_id}")
@inject
def delete_game(
    game_id: str,
    game_service: GameService = Depends(Provide[Container.game_service]),
    current_user: CurrentUser = Depends(get_admin_user),
) -> GameResponseDTO:
    game = game_service.delete_game(game_id)
    return GameResponseDTO(
        id=game.id,
        number=game.number,
        title=game.title,
        description=game.description,
        status=game.status,
        created_at=game.created_at,
        modified_at=game.modified_at,
        opened_at=game.opened_at,
        closed_at=game.closed_at,
        question=game.question,
        # answer=game.answer,
        question_link=game.question_link,
        # answer_link=game.answer_link,
        memo=game.memo,
    )
