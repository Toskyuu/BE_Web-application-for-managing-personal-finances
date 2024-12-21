from datetime import date as dtdate
from typing import Optional

from pydantic import BaseModel, field_validator

from app.database.models.enums import TransactionType, RecurringFrequency


class RecurringTransactionBase(BaseModel):
    description: Optional[str]
    amount: float
    recurring_frequency: RecurringFrequency
    start_date: Optional[dtdate] = None
    next_occurrence: Optional[dtdate] = None

    @field_validator("amount")
    def validate_amount(cls, value):
        if value < 0:
            raise ValueError("Amount should be greater than or equal to 0")
        return value

    @field_validator("start_date")
    def validate_start_date(cls, value):
        if value.year <= 2023:
            raise ValueError("Start date must be after the year 2023.")
        return value

    @field_validator("next_occurrence")
    def validate_next_occurrence(cls, value):
        if value.year <= 2023:
            raise ValueError("Next occurrence must be after the year 2023.")
        return value


class RecurringTransactionCreate(RecurringTransactionBase):
    category_id: int
    account_id: int
    account_id_2: Optional[int] = None
    type: TransactionType


class RecurringTransactionUpdate(RecurringTransactionBase):
    description: Optional[str] = None
    amount: Optional[float] = None
    recurring_frequency: Optional[RecurringFrequency] = None
    start_date: Optional[dtdate] = None
    next_occurrence: Optional[dtdate] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    account_id_2: Optional[int] = None
    type: Optional[TransactionType] = None


class RecurringTransactionList(BaseModel):
    page: Optional[int] = 1
    size: Optional[int] = 10
    sort_by: Optional[str] = "id"
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
        if value and value not in ["id", "amount", "start_date", "recurring_frequency"]:
            raise ValueError("You can only sort by id, amount, start_date or recurring_frequency")
        return value


class RecurringTransaction(BaseModel):
    id: int
    description: Optional[str]
    amount: float
    category_id: int
    account_id: int
    account_id_2: Optional[int] = None
    user_id: int
    start_date: Optional[dtdate] = None
    next_occurrence: Optional[dtdate] = None
    type: TransactionType
    recurring_frequency: RecurringFrequency

    class Config:
        from_attributes = True
