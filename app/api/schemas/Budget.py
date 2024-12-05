from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


class BudgetBase(BaseModel):
    limit: int
    month_year: date
    category_id: int

    @field_validator("month_year")
    def validate_month_year(cls, value):
        if value.year <= 2023:
            raise ValueError("Date must be after the year 2023.")
        return value

    @field_validator("limit")
    def validate_limit(cls, value):
        if value < 0:
            raise ValueError("Limit should be greater than or equal to 0")
        return value


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    limit: Optional[int] = None
    month_year: Optional[date] = None
    category_id: Optional[int] = None


class BudgetUsage(BudgetBase):
    budget_id: int
    user_id: int
    spent_in_budget: float


class Budget(BaseModel):
    budget_id: int
    limit: int
    month_year: date
    category_id: int
    budget_id: int
    user_id: int
    spent_in_budget: float

    class Config:
        from_attributes = True
