from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.User import UserResponse, UserUpdate
from app.database.models.user import User
from app.exceptions.user_exceptions import UserNotFoundError, UserDeleteError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

            await db.delete(user)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            raise UserDeleteError(str(e))

    @staticmethod
    async def update_user(
            db: AsyncSession,
            user_update: UserUpdate,
            user_id: int
    ) -> UserResponse:
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            if user is None:
                raise UserNotFoundError(user_id)

            if user_update.username:
                user.username = user_update.username

            if user_update.email:
                user.email = user_update.email

            await db.commit()
            await db.refresh(user)

            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                is_verified=user.is_verified,
            )

        except SQLAlchemyError as e:
            await db.rollback()
            raise UserDeleteError(str(e))

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> UserResponse:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_verified=user.is_verified,
        )

