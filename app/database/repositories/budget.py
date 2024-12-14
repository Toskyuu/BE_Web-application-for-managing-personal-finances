from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, Budget, BudgetUsage
from app.database.models.budget import Budget as BudgetModel
from app.database.utils import get_spent
from app.database.models.user import User
from app.exceptions.budget_exceptions import BudgetNotFoundError, BudgetUserNotFoundError, BudgetCreationError, \
    BudgetUpdateError, BudgetDeleteError


class BudgetRepository:

    @staticmethod
    async def get_budget(db: AsyncSession, budget_id: int) -> BudgetUsage:
        result = await db.execute(select(BudgetModel).filter(BudgetModel.budget_id == budget_id))
        budget = result.scalars().first()
        if not budget:
            raise BudgetNotFoundError(budget_id)

        return BudgetUsage(
            budget_id=budget.budget_id,
            category_id=budget.category_id,
            limit=budget.limit,
            month_year=budget.month_year,
            user_id=budget.user_id,
            spent_in_budget=await get_spent(db, budget.budget_id)
        )

    @staticmethod
    async def get_budgets_by_user(db: AsyncSession, user_id: int) -> list[BudgetUsage]:
        user = await db.execute(select(User).filter(User.user_id == user_id))
        user = user.scalars().first()
        if not user:
            raise BudgetUserNotFoundError(user_id)

        result = await db.execute(select(BudgetModel).filter(BudgetModel.user_id == user_id))
        budgets = result.scalars().all()

        return [
            BudgetUsage(
                budget_id=budget.budget_id,
                category_id=budget.category_id,
                limit=budget.limit,
                month_year=budget.month_year,
                user_id=budget.user_id,
                spent_in_budget=await get_spent(db, budget.budget_id),
            )
            for budget in budgets
        ]

    @staticmethod
    async def create_budget(db: AsyncSession, budget: BudgetCreate, user_id: int) -> Budget:
        try:
            user = await db.execute(select(User).filter(User.user_id == user_id))
            user = user.scalars().first()
            if not user:
                raise BudgetUserNotFoundError(user_id)

            db_budget = BudgetModel(**budget.model_dump(), user_id=user_id)
            db.add(db_budget)
            await db.commit()
            await db.refresh(db_budget)
            return db_budget
        except SQLAlchemyError as e:
            raise BudgetCreationError(str(e))

    @staticmethod
    async def update_budget(
            db: AsyncSession, budget_id: int, budget_update: BudgetUpdate) -> Budget:
        try:
            async with db.begin():
                result = await db.execute(select(BudgetModel).filter(BudgetModel.budget_id == budget_id))
                budget = result.scalars().first()
                if not budget:
                    raise BudgetNotFoundError(budget_id)

                updated_budget = budget_update.model_dump(exclude_unset=True)

                for key, value in updated_budget.items():
                    setattr(budget, key, value)

            return await db.execute(select(BudgetModel).filter(BudgetModel.budget_id == budget_id)).scalars().first()
        except SQLAlchemyError as e:
            raise BudgetUpdateError(str(e))

    @staticmethod
    async def delete_budget(db: AsyncSession, budget_id: int) -> bool:
        try:
            async with db.begin():
                result = await db.execute(select(BudgetModel).filter(BudgetModel.budget_id == budget_id))
                budget = result.scalars().first()
                if not budget:
                    raise BudgetNotFoundError(budget_id)

                await db.delete(budget)
                return True
        except SQLAlchemyError as e:
            raise BudgetDeleteError(str(e))
