from datetime import timedelta
import pytz
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from containers import Container
from answer.application.answer_service import AnswerService
from game.application.game_service import GameService
from answer.interface.dtos.answer_dto import (
    AnswerRequestDTO,
    AnswerResponseDTO,
    AnswerResponseListDTO,
    AnswerUserResponseDTO,
    AnswerUpdateDTO,
)
from common.auth import get_current_user, CurrentUser, Role
from user.application.user_service import UserService
from user.interface.dtos.user_dto import UserResponseDTO


router = APIRouter(prefix="/answer", tags=["answer"])


@router.post("", response_model=AnswerResponseDTO)
@inject
async def submit_answer(
    body: AnswerRequestDTO,
    user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
    game_service: GameService = Depends(Provide[Container.game_service]),
):
    submitted_answers = answer_service.get_unused_answers_by_game_and_user(
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
        if answer.is_correct and game_service.get_game(body.game_id).closed_at is None:
            game = game_service.update_game_closing_time(
                game_id=body.game_id,
                closed_at=answer.solved_at.astimezone(tz=pytz.timezone("Asia/Seoul"))
                + timedelta(hours=11),
            )

        return AnswerResponseDTO(
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


@router.get("/{answer_id}", response_model=AnswerResponseDTO)
@inject
async def get_answer(
    answer_id: str,
    _: CurrentUser = Depends(get_current_user),  # 인증된 사용자만 접근 가능
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    try:
        answer = answer_service.get_answer(answer_id)
        return AnswerResponseDTO(
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


@router.get("/game/{game_id}")
@inject
async def get_answers_by_game(
    game_id: str,
    _: CurrentUser = Depends(get_current_user),  # 인증된 사용자만 접근 가능
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    try:
        answers = answer_service.get_answers_by_game(game_id)

        # 사용자 정보 포함한 응답 생성
        answer_dtos = []
        for answer in answers:
            # 사용자 정보 처리
            user_dto = None
            if hasattr(answer, "user") and answer.user is not None:
                user_dto = UserResponseDTO(
                    id=answer.user.get("id"),
                    name=answer.user.get("name"),
                    email=answer.user.get("email"),
                    nickname=answer.user.get("nickname"),
                    point=answer.user.get("point"),
                )

            # AnswerUserResponseDTO 생성
            answer_dto = AnswerUserResponseDTO(
                id=answer.id,
                game_id=answer.game_id,
                user_id=answer.user_id,
                answer=answer.answer,
                is_correct=answer.is_correct,
                solved_at=answer.solved_at,
                created_at=answer.created_at,
                updated_at=answer.updated_at,
                point=answer.point,
                user=user_dto,
            )
            answer_dtos.append(answer_dto)

        return {"answers": answer_dtos, "total_count": len(answer_dtos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=AnswerResponseListDTO)
@inject
async def get_answers_by_user(
    current_user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    # 자신의 답변만 조회 가능

    try:
        answers = answer_service.get_answers_by_user(current_user.id)
        return AnswerResponseListDTO(
            answers=[
                AnswerResponseDTO(
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
            ],
            total_count=len(answers),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/game/{game_id}/user", response_model=AnswerUserResponseDTO | None)
@inject
async def get_corrected_answer_by_game_and_user(
    game_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):

    return answer_service.get_corrected_answer_by_game_and_user(
        game_id, current_user.id
    )


@router.get("/game/{game_id}/user/unused", response_model=list[AnswerResponseDTO])
@inject
async def get_unused_answer_by_game_and_user(
    game_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    answers = answer_service.get_unused_answers_by_game_and_user(
        game_id, current_user.id
    )
    if answers is None:
        return []
    return [
        AnswerResponseDTO(
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


@router.post("/empty", response_model=AnswerResponseDTO)
@inject
async def create_empty_answer(
    game_id: str,
    user_id: str,
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
):
    """
    Create an empty answer for admin purposes.
    This endpoint should be protected and only accessible by admin users.
    """
    answer = answer_service.create_answer(game_id=game_id, user_id=user_id)
    return AnswerResponseDTO(
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


@router.post("/all")
@inject
def create_answer_for_all_users_per_game(
    game_id: str,
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
    count: int = 1,
):
    """
    Create Answers for every users.
    If you want make 2 chances, you need to use this api twice.
    """
    res = answer_service.create_answer_for_all_users_per_game(game_id, count)

    # TODO Response 수정해두기
    if res:
        return {200: "Success"}
    return {500: "Failed"}


@router.put("/{answer_id}")
@inject
def update_answer(
    answer_id: str,
    body: AnswerUpdateDTO,
    current_user: CurrentUser = Depends(get_current_user),
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
) -> AnswerResponseDTO:
    try:
        # 기존 답변 조회
        answer = answer_service.get_answer(answer_id)

        # 답변 업데이트
        if body.answer is not None:
            answer.answer = body.answer

        # 점수 업데이트
        if body.point is not None:
            answer.point = body.point

        # 업데이트된 답변 저장
        updated_answer = answer_service.update_answer(answer_id, answer)

        return AnswerResponseDTO(
            id=updated_answer.id,
            game_id=updated_answer.game_id,
            user_id=updated_answer.user_id,
            answer=updated_answer.answer,
            is_correct=updated_answer.is_correct,
            solved_at=updated_answer.solved_at,
            created_at=updated_answer.created_at,
            updated_at=updated_answer.updated_at,
            point=updated_answer.point,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{game_id}/ranking")
@inject
def get_game_ranking(
    game_id: str,
    answer_service: AnswerService = Depends(Provide[Container.answer_service]),
) -> list[AnswerUserResponseDTO]:
    domain_answers = answer_service.get_corrected_answers_by_game(game_id=game_id)

    # 도메인 모델을 DTO로 변환
    answer_dtos = []
    for answer in domain_answers:
        answer_dict = answer.__dict__.copy()

        # user 정보가 있으면 처리
        if hasattr(answer, "user") and answer.user is not None:
            from user.interface.dtos.user_dto import UserResponseDTO

            user_dto = UserResponseDTO(
                id=answer.user.get("id"),
                name="",  # 이름 정보가 없으므로 빈 문자열로 설정
                nickname=answer.user.get("nickname"),
            )
            answer_dict["user"] = user_dto
            answer_dtos.append(AnswerUserResponseDTO.model_validate(answer_dict))

    return answer_dtos
