from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from containers import Container
from user.application.active_user_service import ActiveUserService

router = APIRouter(prefix="/active-users", tags=["active-users"])

@router.get("/count")
@inject
async def get_active_users_count(
    active_user_service: ActiveUserService = Depends(Provide[Container.active_user_service])
):
    """현재 활성 사용자 수를 반환하는 REST API 엔드포인트"""
    count = active_user_service.get_active_users_count()
    return {"count": count}

@router.get("/list")
@inject
async def get_active_users_list(
    active_user_service: ActiveUserService = Depends(Provide[Container.active_user_service])
):
    """현재 활성 사용자 목록을 반환하는 REST API 엔드포인트"""
    users = active_user_service.get_active_users()
    return {"users": users}
