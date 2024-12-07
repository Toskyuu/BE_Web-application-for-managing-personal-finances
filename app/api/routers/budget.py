from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, Budget, BudgetUsage
from app.database.repositories.budget import BudgetRepository
from app.exceptions.budget_exceptions import BudgetUserNotFoundError, BudgetNotFoundError, BudgetCreationError, \
    BudgetUpdateError, BudgetDeleteError

budget_router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)


@budget_router.post("/", response_model=Budget)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db), user_id: int = 1):
    try:
        return BudgetRepository.create_budget(db, budget, user_id)
    except BudgetCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except BudgetUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@budget_router.get("/{budget_id}", response_model=BudgetUsage)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    try:
        return BudgetRepository.get_budget(db, budget_id)
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@budget_router.get("/", response_model=list[BudgetUsage])
def list_budgets_by_user(user_id: int, month: int, year: int, db: Session = Depends(get_db)):
    try:
        return BudgetRepository.get_budgets_by_user(db, user_id, month, year)
    except BudgetUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@budget_router.put("/{budget_id}", response_model=Budget)
def update_budget(budget_id: int, budget_update: BudgetUpdate, db: Session = Depends(get_db)):
    try:
        updated_budget = BudgetRepository.update_budget(db, budget_id, budget_update)
        return updated_budget
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BudgetUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))


@budget_router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    try:
        BudgetRepository.delete_budget(db, budget_id)
        return {"message": "Budget deleted successfully"}
    except BudgetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BudgetDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
