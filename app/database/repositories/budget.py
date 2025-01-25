from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, BudgetUsage, BudgetListResponse
from app.database.models.budget import Budget as BudgetModel
from app.database.models.category import Category
from app.database.models.user import User
from app.database.utils import get_spent
from app.exceptions.budget_exceptions import BudgetNotFoundError, BudgetCreationError, \
    BudgetUpdateError, BudgetDeleteError
from app.exceptions.category_exceptions import CategoryNotFoundError
from app.exceptions.user_exceptions import UnauthorizedError, UserNotFoundError


class BudgetRepository:

    @staticmethod
    async def get_budget(db: AsyncSession, budget_id: int, user_id: int) -> BudgetUsage:
        result = await db.execute(select(BudgetModel, Category.name.label("category_name"))
                                  .join(Category, BudgetModel.category_id == Category.id)
                                  .filter(BudgetModel.id == budget_id))
        budget = result.first()
        if not budget:
            raise BudgetNotFoundError(budget_id)
        budget, category_name = budget
        if budget.user_id != user_id:
            raise UnauthorizedError

        return BudgetUsage(
            id=budget.id,
            category_id=budget.category_id,
            limit=budget.limit,
            month_year=budget.month_year,
            user_id=budget.user_id,
            spent_in_budget=await get_spent(db, budget.id),
            category_name=category_name
        )

    @staticmethod
    async def get_budgets_by_user(
            db: AsyncSession,
            user_id: int,
            page: int,
            size: int,
            sort_by: str,
            order: str
    ) -> BudgetListResponse:
        offset = (page - 1) * size
        sort_order = asc if order == "asc" else desc

        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)

        total_budgets_query = await db.execute(
            select(BudgetModel).filter(BudgetModel.user_id == user_id)
        )
        total_budgets_count = len(total_budgets_query.scalars().all())

        result = await db.execute(
            select(BudgetModel, Category.name.label("category_name"))
            .join(Category, BudgetModel.category_id == Category.id)
            .filter(BudgetModel.user_id == user_id)
            .order_by(
                sort_order(getattr(BudgetModel, sort_by))
                if sort_by != "spent_in_budget" else None
            )
            .offset(offset)
            .limit(size)
        )
        budgets = result.fetchall()

        total_pages = max(1, (total_budgets_count + size - 1) // size)

        budgets_with_spent = [
            BudgetUsage(
                id=budget.id,
                category_id=budget.category_id,
                limit=budget.limit,
                month_year=budget.month_year,
                user_id=budget.user_id,
                spent_in_budget=await get_spent(db, budget.id),
                category_name=category_name
            )
            for budget, category_name in budgets
        ]

        if sort_by == "spent_in_budget":
            budgets_with_spent.sort(key=lambda x: x.spent_in_budget, reverse=(order == "desc"))

        return BudgetListResponse(
            budgets=budgets_with_spent,
            current_page=page,
            total_pages=total_pages
        )

    @staticmethod
    async def create_budget(db: AsyncSession, budget: BudgetCreate, user_id: int) -> BudgetUsage:
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)
            category = await db.execute(select(Category).filter(Category.id == budget.category_id))
            category = category.scalars().first()
            if not category:
                raise CategoryNotFoundError(budget.category_id)
            if category.deleted is True:
                raise CategoryNotFoundError(budget.category_id)
            if category.user_id != user_id:
                raise UnauthorizedError

            db_budget = BudgetModel(**budget.model_dump(), user_id=user_id)
            db.add(db_budget)
            await db.commit()
            await db.refresh(db_budget)
            return BudgetUsage(
                id=db_budget.id,
                category_id=db_budget.category_id,
                limit=db_budget.limit,
                month_year=db_budget.month_year,
                user_id=db_budget.user_id,
                spent_in_budget=await get_spent(db, db_budget.id),
                category_name=category.name
            )

        except SQLAlchemyError as e:
            raise BudgetCreationError(str(e))

    @staticmethod
    async def update_budget(
            db: AsyncSession, budget_id: int, budget_update: BudgetUpdate, user_id: int) -> BudgetUsage:
        try:
            result = await db.execute(select(BudgetModel).filter(BudgetModel.id == budget_id))
            budget = result.scalars().first()
            if not budget:
                raise BudgetNotFoundError(budget_id)

            if budget_update.category_id is not None:
                category = await db.execute(select(Category).filter(Category.id == budget_update.category_id))
                category = category.scalars().first()

                if not category:
                    raise CategoryNotFoundError(budget_update.category_id)

                if category.deleted is True:
                    raise CategoryNotFoundError(budget.category_id)

                if category.user_id != user_id:
                    raise UnauthorizedError

            updated_budget = budget_update.model_dump(exclude_unset=True)

            for key, value in updated_budget.items():
                setattr(budget, key, value)

            await db.commit()

            result = await db.execute(
                select(BudgetModel, Category.name.label("category_name"))
                .join(Category, BudgetModel.category_id == Category.id)
                .filter(BudgetModel.id == budget_id))

            budget = result.first()
            budget, category_name = budget

            return BudgetUsage(
                id=budget.id,
                category_id=budget.category_id,
                limit=budget.limit,
                month_year=budget.month_year,
                user_id=budget.user_id,
                spent_in_budget=await get_spent(db, budget.id),
                category_name=category_name
            )
        except SQLAlchemyError as e:
            raise BudgetUpdateError(str(e))

    @staticmethod
    async def delete_budget(db: AsyncSession, budget_id: int, user_id: int) -> bool:
        try:
            result = await db.execute(select(BudgetModel).filter(BudgetModel.id == budget_id))
            budget = result.scalars().first()
            if not budget:
                raise BudgetNotFoundError(budget_id)
            if budget.user_id != user_id:
                raise UnauthorizedError

            await db.delete(budget)
            await db.commit()

            return True
        except SQLAlchemyError as e:
            raise BudgetDeleteError(str(e))
