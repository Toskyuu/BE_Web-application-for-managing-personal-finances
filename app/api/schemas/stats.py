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
