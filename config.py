import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")