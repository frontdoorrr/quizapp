from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import logging

from containers import Container
from user.interface.controllers.user_controller import router as user_router
from game.interface.controllers.game_controller import router as game_router
from answer.interface.controllers.answer_controller import router as answer_router
from inquiry.interface.controllers.inquiry_controller import router as inquiry_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()
container = Container()
container.wire(packages=["user"])
app.container = container

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=user_router)
app.include_router(router=game_router)
app.include_router(router=answer_router)
app.include_router(router=inquiry_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Request body: {await request.body()}")
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": str(await request.body(), "utf-8")},
    )
