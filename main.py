from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from containers import Container
from user.interface.controllers.user_controller import router as user_router
from user.interface.controllers.coin_controller import router as coin_router
from game.interface.controllers.game_controller import router as game_router
from answer.interface.controllers.answer_controller import router as answer_router
from inquiry.interface.controllers.inquiry_controller import router as inquiry_router
from common.exceptions import QuizAppException
from common.error_handlers import (
    quiz_app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
)

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

# Exception Handlers Registration
app.add_exception_handler(QuizAppException, quiz_app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
