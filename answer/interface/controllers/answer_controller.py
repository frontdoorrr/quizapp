from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from dependency_injector.wiring import inject, Provide

from containers import Container
from answer.application.answer_service import AnswerService
from common.auth import get_current_user


router = APIRouter(prefix="/answers", tags=["answers"])


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
    user: dict = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    try:
        answer = answer_service.submit_answer(
            game_id=body.game_id,
            user_id=user["id"],
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
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{answer_id}", response_model=AnswerResponse)
@inject
async def get_answer(
    answer_id: str,
    _=Depends(get_current_user),  # 인증된 사용자만 접근 가능
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
    _=Depends(get_current_user),  # 인증된 사용자만 접근 가능
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
    user_id: str,
    current_user: dict = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    # 자신의 답변만 조회 가능
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=403, detail="You can only view your own answers"
        )

    try:
        answers = answer_service.get_answers_by_user(user_id)
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
