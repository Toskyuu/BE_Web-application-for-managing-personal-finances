from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import User
from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, Budget, BudgetUsage, BudgetList
from app.database.postgres_utils import get_db
from app.database.repositories.budget import BudgetRepository
from app.database.repositories.user_manager import fastapi_users
from app.exceptions.budget_exceptions import (
    BudgetNotFoundError,
    BudgetCreationError,
    BudgetUpdateError,
    BudgetDeleteError
)
from app.exceptions.category_exceptions import CategoryNotFoundError
from app.exceptions.user_exceptions import UnauthorizedError, UserNotFoundError

budget_router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)

current_user = fastapi_users.current_user()


@budget_router.post("/", response_model=Budget)
async def create_budget(budget: BudgetCreate,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(current_user),
                        ):
    try:
        return await BudgetRepository.create_budget(db, budget, user_id=user.id)
    except BudgetCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@budget_router.get("/{budget_id}", response_model=BudgetUsage)
async def get_budget(budget_id: int,
                     db: AsyncSession = Depends(get_db),
                     user: User = Depends(current_user)
                     ):
    try:
        return await BudgetRepository.get_budget(db, budget_id, user_id=user.id)
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@budget_router.post("/budgets", response_model=list[BudgetUsage])
async def list_budgets(
        budget: BudgetList,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await BudgetRepository.get_budgets_by_user(
            db, user_id=user.id, page=budget.page, size=budget.size, sort_by=budget.sort_by, order=budget.order)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@budget_router.patch("/{budget_id}", response_model=Budget)
async def update_budget(budget_id: int,
                        budget_update: BudgetUpdate,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(current_user)
                        ):
    try:
        updated_budget = await BudgetRepository.update_budget(db, budget_id, budget_update, user_id=user.id)
        return updated_budget
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BudgetUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

@budget_router.delete("/{budget_id}")
async def delete_budget(budget_id: int,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(current_user)
                        ):
    try:
        await BudgetRepository.delete_budget(db, budget_id, user_id=user.id)
        return {"message": "Budget deleted successfully"}
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BudgetDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))
