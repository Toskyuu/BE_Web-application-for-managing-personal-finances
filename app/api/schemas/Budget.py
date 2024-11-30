from pydantic import BaseModel
from typing import Optional
from datetime import date



class BudgetBase(BaseModel):
    limit: int
    month_year: date
    category_id: int


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    limit: Optional[int]
    month_year: Optional[date]
    category_id: Optional[int]

class BudgetUsage(BudgetBase):
    budget_id: int
    user_id: int
    spent_in_budget: float

class Budget(BudgetBase):
    budget_id: int
    user_id: int

    class Config:
        from_attributes = True
