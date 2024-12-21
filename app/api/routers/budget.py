from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres_utils import get_db
from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, Budget, BudgetUsage, BudgetList
from app.database.repositories.budget import BudgetRepository
from app.exceptions.budget_exceptions import (
    BudgetUserNotFoundError,
    BudgetNotFoundError,
    BudgetCreationError,
    BudgetUpdateError,
    BudgetDeleteError
)

budget_router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)


@budget_router.post("/", response_model=Budget)
async def create_budget(budget: BudgetCreate, db: AsyncSession = Depends(get_db), user_id: int = 1):
    try:
        return await BudgetRepository.create_budget(db, budget, user_id)
    except BudgetCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except BudgetUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@budget_router.get("/{budget_id}", response_model=BudgetUsage)
async def get_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await BudgetRepository.get_budget(db, budget_id)
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@budget_router.post("/budgets", response_model=list[BudgetUsage])
async def list_budgets_by_user(
        user_id: int,
        budget: BudgetList,
        db: AsyncSession = Depends(get_db)):
    try:
        return await BudgetRepository.get_budgets_by_user(
            db, user_id=user_id, page=budget.page, size=budget.size, sort_by=budget.sort_by, order=budget.order)
    except BudgetUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@budget_router.put("/{budget_id}", response_model=Budget)
async def update_budget(budget_id: int, budget_update: BudgetUpdate, db: AsyncSession = Depends(get_db)):
    try:
        updated_budget = await BudgetRepository.update_budget(db, budget_id, budget_update)
        return updated_budget
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BudgetUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))


@budget_router.delete("/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await BudgetRepository.delete_budget(db, budget_id)
        return {"message": "Budget deleted successfully"}
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BudgetDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
