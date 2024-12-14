from fastapi import Depends
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi_users.db import SQLAlchemyUserDatabase
from app.database.models.user import User
from app.database.postgres_utils import get_db

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
JWT_LIFETIME_SECONDS = int(os.getenv("JWT_LIFETIME_SECONDS", 3600))

cookie_transport = CookieTransport(cookie_name="auth", cookie_max_age=JWT_LIFETIME_SECONDS)

async def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=JWT_LIFETIME_SECONDS)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


