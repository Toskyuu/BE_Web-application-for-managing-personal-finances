from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from app.api.schemas.User import UserCreate, UserRead
from app.database.models.user import User
from app.database.repositories.user_manager import get_user_manager
from app.services.auth import auth_backend

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=False),
)
user_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

user_router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

user_router.include_router(
    fastapi_users.get_reset_password_router(),
)
