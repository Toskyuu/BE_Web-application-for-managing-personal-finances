import os

from dotenv import load_dotenv
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.manager import BaseUserManager

from app.database.models.user import User, get_user_db
from app.services.auth import auth_backend
from app.services.mail import send_verification_email

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


class UserManager(BaseUserManager[User, int]):
    def parse_id(self, id: str):
        try:
            return int(id)
        except ValueError:
            raise ValueError("Invalid user ID format")

    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.email} has registered.")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        await send_verification_email(user.email, "Potwierdź konto", f'To twój token - {token}')

    async def on_after_forgot_password(
            self, user: User, token: str, request=None):
        await send_verification_email(user.email, 'Zresetuj hasło', 'Jeśli to nie ty, to zignoruj tę wiadomość.')




def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
