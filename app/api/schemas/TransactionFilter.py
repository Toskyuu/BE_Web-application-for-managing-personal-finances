from datetime import date
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import field_validator

from app.database.models.enums import TransactionType
from app.database.models.transaction import Transaction


class TransactionFilter(Filter):
    account_id: Optional[List[int]] = None
    category_id: Optional[List[int]] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    type: Optional[List[TransactionType]] = None
    page: Optional[int] = 1
    size: Optional[int] = 10
    sort_by: Optional[str] = "id"
    order: Optional[str] = "desc"

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
            raise ValueError("Sort must be either ascending or descending")
        return value

    @field_validator("sort_by")
    def validate_sort_by(cls, value):
        if value and value not in ["id", "transaction_date", "amount"]:
            raise ValueError("You can only sort by id, transaction_date or amount")
        return value

    class Constants(Filter.Constants):
        model = Transaction
