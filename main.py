from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from user.interface.controllers.user_controller import router as user_routers

app = FastAPI()
app.include_router(router=user_routers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )
