# app/routes/user_routes.py
from fastapi import APIRouter, HTTPException, Header, Depends
from app.schemas.user_schema import UserRegister, UserLogin, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.post("/register", status_code=201)
async def register(user: UserRegister):
    res = await UserService.register_user(user.dict())
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return {"status": "success", "data": res}

@router.post("/login")
async def login(credentials: UserLogin):
    res = await UserService.login_user(credentials.email, credentials.password)
    if "error" in res:
        raise HTTPException(status_code=401, detail=res["error"])
    return {"status": "success", "data": res}

# Protected endpoint helper
async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1].strip()
    user = await UserService.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)):
    # current_user is already a dict without password
    return current_user
