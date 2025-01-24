from datetime import date as dtdate
from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.database.models.enums import TransactionType, Interval


class TransactionsOverTimeFilter(BaseModel):
    account_id: Optional[List[int]] = None
    category_id: Optional[List[int]] = None
    date_from: Optional[dtdate] = None
    date_to: Optional[dtdate] = None
    type: Optional[List[TransactionType]] = None
    interval: Optional[Interval] = 'Monthly'

    @field_validator("interval")
    def validate_size(cls, value):
        if value and value not in ["Monthly", "Daily", "Yearly"]:
            raise ValueError("You can set interval only to  Daily, Monthly or Yearly")
        return value


class ExpenseComparisonItem(BaseModel):
    time_group: str
    expenses: float
    incomes: float


class TransactionsOverTimeResponse(BaseModel):
    data: List[ExpenseComparisonItem]
    total_count: int


class BaseStatFilter(BaseModel):
    account_id: Optional[List[int]] = None
    category_id: Optional[List[int]] = None
    date_from: Optional[dtdate] = None
    date_to: Optional[dtdate] = None
    type: Optional[TransactionType] = "Outcome"


class CategoriesSpentItem(BaseModel):
    category: str
    expenses: float
    incomes: float
    expense_count: int
    income_count: int


class CategoriesSpentResponse(BaseModel):
    data: List[CategoriesSpentItem]
    start_date: dtdate
    end_date: dtdate
    type: TransactionType



class SummaryResponse(BaseModel):
    expenses: float
    incomes: float
    expense_count: int
    income_count: int
    start_date: dtdate
    end_date: dtdate



class CumulativeItem(BaseModel):
    date: dtdate
    cumulative_income: float
    cumulative_expense: float
    cumulative_income_count: int
    cumulative_expense_count: int

class CumulativeResponse(BaseModel):
    data: List[CumulativeItem]
    start_date: dtdate
    end_date: dtdate
