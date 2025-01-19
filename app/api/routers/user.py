from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import User
from app.api.schemas.User import UserCreate, UserRead, UserResponse, UserUpdate
from app.database.postgres_utils import get_db
from app.database.repositories.user import UserRepository
from app.database.repositories.user_manager import fastapi_users
from app.exceptions.user_exceptions import UserNotFoundError, UserDeleteError, UserUpdateError
from app.services.auth import auth_backend

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

current_user = fastapi_users.current_user()

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

@user_router.patch("/me", response_model=UserResponse)
async def update_user(user_to_update: UserUpdate, user: User = Depends(current_user),
                      db: AsyncSession = Depends(get_db)):
    try:
        updated_user = await UserRepository.update_user(db, user_to_update, user_id=user.id)
        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.delete("/me")
async def delete_user(user: User = Depends(current_user),
                      db: AsyncSession = Depends(get_db)):
    try:
        await UserRepository.delete_user(db, user_id=user.id)
        return {"message": "User deleted successfully"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDeleteError as e:
        raise HTTPException(status_code=400, detail=str(e))

@user_router.get("/me")
async def get_user(user: User = Depends(current_user),
                      db: AsyncSession = Depends(get_db)) -> UserResponse:
    try:
        response = await UserRepository.get_user(db, user_id=user.id)
        return response
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


