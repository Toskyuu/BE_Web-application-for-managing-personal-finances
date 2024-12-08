from datetime import date as dtdate
from typing import Optional

from pydantic import BaseModel, field_validator

from app.database.models.enums import TransactionType, RecurringFrequency


class TransactionBase(BaseModel):
    description: Optional[str]
    amount: float
    date: Optional[dtdate] = None

    @field_validator("amount")
    def validate_amount(cls, value):
        if value < 0:
            raise ValueError("Amount should be greater than or equal to 0")
        return value

    @field_validator("date")
    def validate_date(cls, value):
        if value and value.year <= 2023:
            raise ValueError("Date must be after the year 2023.")
        return value


class TransactionCreate(TransactionBase):
    category_id: int
    account_id: int
    account_id_2: Optional[int] = None
    type: TransactionType
    is_recurring: Optional[bool] = False
    recurring_frequency: Optional[RecurringFrequency] = None
    next_occurrence: Optional[dtdate] = None



class TransactionUpdate(TransactionBase):
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[dtdate] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    account_id_2: Optional[int] = None
    type: Optional[TransactionType] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[RecurringFrequency] = None
    next_occurrence: Optional[dtdate] = None


class Transaction(BaseModel):
    transaction_id: int
    category_id: int
    account_id: int
    account_id_2: Optional[int] = None
    user_id: int
    date: dtdate
    type: TransactionType
    is_recurring: Optional[bool] = False
    recurring_frequency: Optional[RecurringFrequency] = None
    next_occurrence: Optional[dtdate] = None

    class Config:
        from_attributes = True
