# app/models/user_model.py
from datetime import datetime

def make_user_doc(data: dict) -> dict:
    return {
        "name": data["name"],
        "email": data["email"],
        "phone": data.get("phone"),
        "password": data["password"],  # hashed
        "roles": data.get("roles", ["user"]),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
