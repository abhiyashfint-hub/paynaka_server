# app/services/user_service.py
from typing import Optional
from bson import ObjectId
from app.core.database import db
from app.models.user_model import make_user_doc
from passlib.context import CryptContext
from app.core.security import create_access_token, verify_token

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
users = db["users"]

class UserService:
    @staticmethod
    async def hash_password(password: str) -> str:
        return pwd_ctx.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_ctx.verify(plain, hashed)

    @staticmethod
    async def register_user(data: dict) -> dict:
        # check duplicate email
        existing = await users.find_one({"email": data["email"]})
        if existing:
            return {"error": "Email already registered"}

        data["password"] = await UserService.hash_password(data["password"])
        user_doc = make_user_doc(data)
        result = await users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        return {"id": user_id, "message": "User registered successfully"}

    @staticmethod
    async def login_user(email: str, password: str) -> dict:
        user = await users.find_one({"email": email})
        if not user or not UserService.verify_password(password, user["password"]):
            return {"error": "Invalid credentials"}
        token = create_access_token({"user_id": str(user["_id"]), "email": user["email"]})
        return {"access_token": token, "token_type": "bearer"}

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[dict]:
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            return None
        user = await users.find_one({"_id": obj_id}, {"password": 0})
        if not user:
            return None
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        return user

    @staticmethod
    async def get_user_by_token(token: str) -> Optional[dict]:
        payload = verify_token(token)
        if not payload:
            return None
        user_id = payload.get("user_id")
        if not user_id:
            return None
        return await UserService.get_user_by_id(user_id)
