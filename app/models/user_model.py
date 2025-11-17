from datetime import datetime

def user_document():
    return {
        "name": "",
        "email": "",
        "phone": "",
        "password": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
