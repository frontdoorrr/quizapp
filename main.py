from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from containers import Container
from user.interface.controllers.user_controller import router as user_routers
from game.interface.controllers.game_controller import router as game_routers

app = FastAPI()
container = Container()
container.wire(packages=["user"])
app.container = container

app.include_router(router=user_routers)
app.include_router(router=game_routers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )
