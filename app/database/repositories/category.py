from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.Category import CategoryUpdate, CategoryCreate
from app.database.models.category import Category
from app.database.models.user import User
from app.exceptions.category_exceptions import CategoryNotFoundError, CategoryUserNotFoundError, CategoryCreationError, \
    CategoryUpdateError, CategoryDeleteError


class CategoryRepository:
    @staticmethod
    async def get_category(db: AsyncSession, category_id: int):
        result = await db.execute(select(Category).filter(
            Category.category_id == category_id,
            Category.deleted == False
        ))
        category = result.scalars().first()
        if not category:
            raise CategoryNotFoundError(category_id)
        return category

    @staticmethod
    async def get_categories_by_user(db: AsyncSession, user_id: int):
        result = await db.execute(select(User).filter(User.user_id == user_id))
        user = result.scalars().first()
        if not user:
            raise CategoryUserNotFoundError(user_id)

        result = await db.execute(select(Category).filter(
            Category.user_id == user_id,
            Category.deleted == False
        ))
        return result.scalars().all()

    @staticmethod
    async def create_category(db: AsyncSession, category: CategoryCreate, user_id: int):
        try:
            result = await db.execute(select(User).filter(User.user_id == user_id))
            user = result.scalars().first()
            if not user:
                raise CategoryUserNotFoundError(user_id)

            db_category = Category(**category.model_dump(), user_id=user_id)
            db.add(db_category)
            await db.commit()
            await db.refresh(db_category)
            return db_category
        except SQLAlchemyError as e:
            raise CategoryCreationError(str(e))

    @staticmethod
    async def update_category(
            db: AsyncSession, category_id: int, category_update: CategoryUpdate) -> Category:
        try:
            async with db.begin():
                result = await db.execute(select(Category).filter(Category.category_id == category_id))
                category = result.scalars().first()
                if not category:
                    raise CategoryNotFoundError(category_id)

                updated_category = category_update.model_dump(exclude_unset=True)

                for key, value in updated_category.items():
                    setattr(category, key, value)

            result = await db.execute(select(Category).filter(Category.category_id == category_id))
            return result.scalars().first()

        except SQLAlchemyError as e:
            raise CategoryUpdateError(str(e))

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> bool:
        try:
            async with db.begin():
                result = await db.execute(select(Category).filter(Category.category_id == category_id))
                category = result.scalars().first()
                if not category:
                    raise CategoryNotFoundError(category_id)

                category.deleted = True
                return True
        except SQLAlchemyError as e:
            raise CategoryDeleteError(str(e))
