import os
from fastapi_login import LoginManager
from dotenv import load_dotenv
from passlib.hash import bcrypt

load_dotenv()
SECRET = os.getenv("AUTH_SECRET", "supersecret")

manager = LoginManager(SECRET, "/login", use_cookie=True)

# Base de datos falsa en memoria
fake_users_db = {
    "edu": {
        "name": "Edu",
        "password": "$2b$12$ZH/r8YbsxAX2T093BEcm8.6gGWKetLmRTlnq/04QujwDELYCbage6",
        "tools": ["get_weather", "saludar", "send_email"]
    }
}

@manager.user_loader()
def load_user(username: str):
    return fake_users_db.get(username)
