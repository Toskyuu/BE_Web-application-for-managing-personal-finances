from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, Budget, BudgetUsage
from app.database.repositories.budget import BudgetRepository

budget_router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)


@budget_router.post("/", response_model=Budget)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db), user_id: int = 1):
    try:
        return BudgetRepository.create_budget(db, budget, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@budget_router.get("/{budget_id}", response_model=BudgetUsage)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = BudgetRepository.get_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@budget_router.get("/", response_model=list[BudgetUsage])
def list_budgets_by_user(user_id: int, month: int, year: int, db: Session = Depends(get_db)):
    return BudgetRepository.get_budgets_by_user(db, user_id, month, year)


@budget_router.put("/{budget_id}", response_model=Budget)
def update_budget(budget_id: int, budget_update: BudgetUpdate, db: Session = Depends(get_db)):
    try:
        updated_budget = BudgetRepository.update_budget(db, budget_id, budget_update)
        if not updated_budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return updated_budget
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@budget_router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    success = BudgetRepository.delete_budget(db, budget_id)
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted successfully"}
