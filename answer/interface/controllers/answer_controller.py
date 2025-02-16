from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from game.application import game_service
from pydantic import BaseModel, Field
from dependency_injector.wiring import inject, Provide

from containers import Container
from answer.application.answer_service import AnswerService
from game.application.game_service import GameService
from common.auth import get_current_user, CurrentUser
from answer.domain.exceptions import InsufficientCoinError


router = APIRouter(prefix="/answer", tags=["answer"])


class SubmitAnswerBody(BaseModel):
    game_id: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class AnswerResponse(BaseModel):
    id: str
    game_id: str
    user_id: str
    answer: str
    is_correct: bool
    solved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    point: int


@router.post("", response_model=AnswerResponse)
@inject
async def submit_answer(
    body: SubmitAnswerBody,
    user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    submitted_answers = answer_service.get_answers_by_game_and_user(
        body.game_id, user.id
    )
    if not submitted_answers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted an answer for this game",
        )

    for submitted_answer in submitted_answers:
        if submitted_answer.is_correct:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already correctly submitted an answer for this game",
            )

    try:
        answer = answer_service.submit_answer(
            game_id=body.game_id,
            user_id=user.id,
            answer_text=body.answer,
        )
        return AnswerResponse(
            id=answer.id,
            game_id=answer.game_id,
            user_id=answer.user_id,
            answer=answer.answer,
            is_correct=answer.is_correct,
            solved_at=answer.solved_at,
            created_at=answer.created_at,
            updated_at=answer.updated_at,
            point=answer.point,
        )
    except InsufficientCoinError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Insufficient coins to submit answer",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{answer_id}", response_model=AnswerResponse)
@inject
async def get_answer(
    answer_id: str,
    _: CurrentUser = Depends(get_current_user),  # 인증된 사용자만 접근 가능
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    try:
        answer = answer_service.get_answer(answer_id)
        return AnswerResponse(
            id=answer.id,
            game_id=answer.game_id,
            user_id=answer.user_id,
            answer=answer.answer,
            is_correct=answer.is_correct,
            solved_at=answer.solved_at,
            created_at=answer.created_at,
            updated_at=answer.updated_at,
            point=answer.point,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/game/{game_id}", response_model=list[AnswerResponse])
@inject
async def get_answers_by_game(
    game_id: str,
    _: CurrentUser = Depends(get_current_user),  # 인증된 사용자만 접근 가능
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    try:
        answers = answer_service.get_answers_by_game(game_id)
        return [
            AnswerResponse(
                id=answer.id,
                game_id=answer.game_id,
                user_id=answer.user_id,
                answer=answer.answer,
                is_correct=answer.is_correct,
                solved_at=answer.solved_at,
                created_at=answer.created_at,
                updated_at=answer.updated_at,
                point=answer.point,
            )
            for answer in answers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=list[AnswerResponse])
@inject
async def get_answers_by_user(
    current_user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    # 자신의 답변만 조회 가능

    try:
        answers = answer_service.get_answers_by_user(current_user.id)
        return [
            AnswerResponse(
                id=answer.id,
                game_id=answer.game_id,
                user_id=answer.user_id,
                answer=answer.answer,
                is_correct=answer.is_correct,
                solved_at=answer.solved_at,
                created_at=answer.created_at,
                updated_at=answer.updated_at,
                point=answer.point,
            )
            for answer in answers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/game/{game_id}/user", response_model=AnswerResponse | None)
@inject
async def get_answer_by_game_and_user(
    game_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):

    return answer_service.get_answer_by_game_and_user(game_id, current_user.id)


@router.delete("/game/current/user")
@inject
async def delete_answer_by_game_and_user(
    current_user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    """Delete current user's answer for the current game

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if answer not found
        HTTPException: 404 if current game not found
    """
    try:
        game = game_service.get_current_game()
        answer_service.delete_answer_by_game_and_user(game.id, current_user.id)
        return {"message": "Answer deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
