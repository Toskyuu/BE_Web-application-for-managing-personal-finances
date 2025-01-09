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
    id: int
    user_id: int
    spent_in_budget: float


class BudgetList(BaseModel):
    page: Optional[int] = 1
    size: Optional[int] = 10
    sort_by: Optional[str] = "month_year"
    order: Optional[str] = "asc"

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
        if value and value not in ["month_year", "limit", "spent_in_budget"]:
            raise ValueError("You can only sort by month_year, limit or spent_in_budget")
        return value


class Budget(BaseModel):
    id: int
    limit: int
    month_year: date
    category_id: int
    user_id: int
    spent_in_budget: Optional[float] = None

    class Config:
        from_attributes = True
