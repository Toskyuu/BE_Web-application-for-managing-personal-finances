from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.Category import CategoryUpdate, CategoryCreate
from app.database.models.category import Category
from app.database.models.user import User
from app.exceptions.category_exceptions import CategoryNotFoundError, CategoryCreationError, \
    CategoryUpdateError, CategoryDeleteError
from app.exceptions.user_exceptions import UnauthorizedError, UserNotFoundError


class CategoryRepository:
    @staticmethod
    async def get_category(db: AsyncSession, category_id: int, user_id: int) -> Category:
        result = await db.execute(select(Category).filter(
            Category.id == category_id,
            Category.deleted == False
        ))
        category = result.scalars().first()
        if not category:
            raise CategoryNotFoundError(category_id)
        if category.user_id != user_id:
            raise UnauthorizedError
        return category

    @staticmethod
    async def get_categories_by_user(
            db: AsyncSession,
            user_id: int,
            page: int,
            size: int,
            sort_by: str,
            order: str
    ):
        sort_order = asc if order == "asc" else desc

        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)

        if page and size:
            offset = (page - 1) * size
            result = await db.execute(
                select(Category).
                filter(
                    Category.user_id == user_id,
                    Category.deleted == False
                )
                .order_by(sort_order(getattr(Category, sort_by)))
                .offset(offset)
                .limit(size)
            )
        else:
            result = await db.execute(
                select(Category).
                filter(
                    Category.user_id == user_id,
                    Category.deleted == False
                )
                .order_by(sort_order(getattr(Category, sort_by))))

        return result.scalars().all()

    @staticmethod
    async def create_category(db: AsyncSession, category: CategoryCreate, user_id: int):
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

            db_category = Category(**category.model_dump(), user_id=user_id)
            db.add(db_category)
            await db.commit()
            await db.refresh(db_category)
            return db_category
        except SQLAlchemyError as e:
            raise CategoryCreationError(str(e))

    @staticmethod
    async def update_category(
            db: AsyncSession, category_id: int, category_update: CategoryUpdate, user_id: int) -> Category:
        try:
            result = await db.execute(select(Category).filter(Category.id == category_id))
            category = result.scalars().first()
            if not category:
                raise CategoryNotFoundError(category_id)
            if category.deleted is True:
                raise CategoryNotFoundError(category_id)
            if category.user_id != user_id:
                raise UnauthorizedError

            updated_category = category_update.model_dump(exclude_unset=True)

            for key, value in updated_category.items():
                setattr(category, key, value)

            await db.commit()

            result = await db.execute(select(Category).filter(Category.id == category_id))
            return result.scalars().first()

        except SQLAlchemyError as e:
            raise CategoryUpdateError(str(e))

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> bool:
        try:
            result = await db.execute(select(Category).filter(Category.id == category_id))
            category = result.scalars().first()
            if not category:
                raise CategoryNotFoundError(category_id)
            if category.user_id != user_id:
                raise UnauthorizedError

            category.deleted = True
            await db.commit()
            return True
        except SQLAlchemyError as e:
            raise CategoryDeleteError(str(e))
