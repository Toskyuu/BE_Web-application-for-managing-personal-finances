from fastapi import Depends
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend, BearerTransport
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

bearer_transport = BearerTransport(tokenUrl="users/login")

async def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=JWT_LIFETIME_SECONDS)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


