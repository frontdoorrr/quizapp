from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
import logging

from containers import Container
from user.interface.controllers.user_controller import router as user_router
from user.interface.controllers.coin_controller import router as coin_router
from game.interface.controllers.game_controller import router as game_router
from answer.interface.controllers.answer_controller import router as answer_router
from inquiry.interface.controllers.inquiry_controller import router as inquiry_router
from user.interface.controllers.active_user_controller import router as active_user_router
from common.exceptions import QuizAppException
from common.error_handlers import (
    quiz_app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
)
from common.middleware.active_users import ActiveUserMiddleware

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI(
    title="Quiz App API",
    description="Quiz Application API",
    version="1.0.0"
)

# Dependency Injection Container
container = Container()
container.wire(packages=["user", "game", "answer", "inquiry"])
app.container = container

# Router Registration
app.include_router(router=user_router)
app.include_router(router=coin_router)
app.include_router(router=game_router)
app.include_router(router=answer_router)
app.include_router(router=inquiry_router)
app.include_router(router=active_user_router)

# 미들웨어 등록
app.add_middleware(ActiveUserMiddleware)

# # CORS 설정
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 실제 배포 환경에서는 구체적인 출처로 제한하는 것이 좋습니다
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Exception Handlers Registration
app.add_exception_handler(QuizAppException, quiz_app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# 애플리케이션 시작 시 활성 사용자 서비스의 백그라운드 업데이터 시작
@app.on_event("startup")
def startup_event():
    active_user_service = container.active_user_service()
    active_user_service.start_background_updater()
    logger.info("활성 사용자 서비스 백그라운드 업데이터 시작")


# 애플리케이션 종료 시 활성 사용자 서비스의 백그라운드 업데이터 중지
@app.on_event("shutdown")
def shutdown_event():
    active_user_service = container.active_user_service()
    active_user_service.stop_background_updater()
    logger.info("활성 사용자 서비스 백그라운드 업데이터 중지")
