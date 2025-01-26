from datetime import date
from typing import Optional, List

from pydantic import BaseModel, field_validator


class BudgetBase(BaseModel):
    limit: float
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
            raise ValueError("Limit should be greater than 0")
        return value


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    limit: Optional[float] = None
    month_year: Optional[date] = None
    category_id: Optional[int] = None


class BudgetUsage(BudgetBase):
    id: int
    user_id: int
    spent_in_budget: float
    category_name: str
    spent_to_limit_ratio: Optional[float]


class BudgetList(BaseModel):
    page: Optional[int] = 1
    size: Optional[int] = 10
    sort_by: Optional[str] = "month_year"
    order: Optional[str] = "asc"
    month_year: Optional[date] = None
    category_id: Optional[List[int]] = None

    @field_validator("page")
    def validate_page(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Page number must be greater than 0")
        return value

    @field_validator("size")
    def validate_size(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Size must be at least 1")
        return value

    @field_validator("order")
    def validate_order(cls, value):
        if value and value not in ["asc", "desc"]:
            raise ValueError("Sort must be either asc or desc")
        return value

    @field_validator("sort_by")
    def validate_sort_by(cls, value):
        if value and value not in ["month_year", "limit", "spent_to_limit_ratio", "spent_in_budget"]:
            raise ValueError("You can only sort by month_year, limit, spent_to_limit_ratio or spent_in_budget")
        return value


class Budget(BaseModel):
    id: int
    limit: float
    month_year: date
    category_id: int
    user_id: int
    spent_in_budget: Optional[float] = None
    category_name: str

    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    budgets: List[BudgetUsage]
    current_page: int
    total_pages: int
