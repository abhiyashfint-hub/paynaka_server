import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    def __init__(self):
        self.MONGO_URL = os.getenv("MONGO_URL")

settings = Settings()
