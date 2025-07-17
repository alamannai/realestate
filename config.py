from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    CORS_ORIGINS = "http://localhost:8080"