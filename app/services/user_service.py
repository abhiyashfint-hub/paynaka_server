from fastapi import HTTPException
from passlib.context import CryptContext
from bson import ObjectId
from app.core.database import db
from app.core.auth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection = db["users"]

class UserService:

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain, hashed):
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def register(user):
        # Check duplicate email
        if users_collection.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = UserService.hash_password(user.password)

        user_dict = {
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "password": hashed_pw
        }

        result = users_collection.insert_one(user_dict)
        return {"id": str(result.inserted_id), "message": "User registered successfully"}

    @staticmethod
    def login(user):
        db_user = users_collection.find_one({"email": user.email})
        if not db_user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not UserService.verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token({"user_id": str(db_user["_id"])})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    @staticmethod
    def get_profile(user_id: str):
        user = users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user["id"] = str(user["_id"])
        del user["_id"]
        return user
