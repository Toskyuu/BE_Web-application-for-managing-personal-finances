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
    end_date: Optional[dtdate] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    account_id_2: Optional[int] = None
    type: Optional[TransactionType] = None


class RecurringTransaction(BaseModel):
    recurring_transaction_id: int
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
