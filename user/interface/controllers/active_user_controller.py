from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from containers import Container
from user.application.active_user_service import ActiveUserService

router = APIRouter(prefix="/active-users", tags=["active-users"])


@router.get("/count")
@inject
async def get_active_users_count(
    active_user_service: ActiveUserService = Depends(
        Provide[Container.active_user_service]
    ),
):
    """현재 활성 사용자 수를 반환하는 REST API 엔드포인트"""
    count = active_user_service.get_active_users_count()
    return {"count": count}


@router.get("/list")
@inject
async def get_active_users_list(
    active_user_service: ActiveUserService = Depends(
        Provide[Container.active_user_service]
    ),
):
    """현재 활성 사용자 목록을 반환하는 REST API 엔드포인트 (닉네임만 반환)"""
    users = active_user_service.get_active_users()

    # 닉네임만 필터링하여 반환
    filtered_users = []
    for user in users:
        if "nickname" in user:
            filtered_users.append({"nickname": user["nickname"]})
        else:
            # 닉네임이 없는 경우 빈 값으로 처리
            filtered_users.append({"nickname": ""})

    return {"users": filtered_users}
