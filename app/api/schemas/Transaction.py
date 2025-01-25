from datetime import date as dtdate
from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.database.models.enums import TransactionType, RecurringFrequency


class TransactionBase(BaseModel):
    description: Optional[str]
    amount: float
    transaction_date: Optional[dtdate] = None

    @field_validator("amount")
    def validate_amount(cls, value):
        if value < 0:
            raise ValueError("Amount should be greater than or equal to 0")
        return value

    @field_validator("transaction_date")
    def validate_date(cls, value):
        if value and value.year <= 2023:
            raise ValueError("Date must be after the year 2023.")
        return value


class TransactionCreate(TransactionBase):
    category_id: int
    account_id: int
    account_id_2: Optional[int] = None
    type: TransactionType


class TransactionUpdate(TransactionBase):
    description: Optional[str] = None
    amount: Optional[float] = None
    transaction_date: Optional[dtdate] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    account_id_2: Optional[int] = None
    type: Optional[TransactionType] = None


class Transaction(BaseModel):
    id: int
    category_id: int
    category_name: str
    account_id: int
    account_name: str
    account_id_2: Optional[int] = None
    account_2_name: Optional[str] = None
    user_id: int
    transaction_date: dtdate
    type: TransactionType
    amount: float
    description: str


    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    transaction: Transaction
    recurring_frequency: Optional[RecurringFrequency]

class TransactionListResponse(BaseModel):
    transactions: List[Transaction]
    current_page: int
    total_pages: int

