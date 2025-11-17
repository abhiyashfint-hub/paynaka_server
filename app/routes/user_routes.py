from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserRegister, UserLogin
from app.services.user_service import UserService

router = APIRouter()

@router.post("/register")
def register_user(data: UserRegister):
    return UserService.register(data)

@router.post("/login")
def login_user(data: UserLogin):
    return UserService.login(data)

@router.get("/profile/{user_id}")
def user_profile(user_id: str):
    return UserService.get_profile(user_id)
