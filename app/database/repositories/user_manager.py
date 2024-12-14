import os

from dotenv import load_dotenv
from fastapi import Depends
from fastapi_users.manager import BaseUserManager

from app.database.models.user import User, get_user_db

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.email} has registered.")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        print(f"Verification token for user {user.email}: {token}")


def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
