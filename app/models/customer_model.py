from beanie import Document
from pydantic import Field
from datetime import datetime

class Customer(Document):
    name: str
    phone: str
    vendor_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customers"
