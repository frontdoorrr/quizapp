from fastapi import FastAPI

from user.interface.controllers.user_controller import router as user_routers

app = FastAPI()
app.include_router(router=user_routers)
