from fastapi import APIRouter

router = APIRouter(prefix="/users")


@router.post("", status_code=201)
def create_user():
    return "User Created"
