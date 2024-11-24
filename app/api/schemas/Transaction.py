import datetime

from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.database.models.enums import TransactionType


class TransactionBase(BaseModel):
    description: Optional[str]
    amount: float
    date: Optional[date] = None


class TransactionCreateBase(TransactionBase):
    category_id: int


class TransactionCreateOutcome(TransactionCreateBase):
    from_account_id: int

class TransactionCreateIncome(TransactionCreateBase):
    to_account_id: int


class TransactionCreateInternal(TransactionCreateBase):
    from_account_id: int
    to_account_id: int

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    category_id: Optional[int] = None
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None


class Transaction(TransactionBase):
    transaction_id: int
    category_id: int
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    user_id: int
    date: Optional[datetime.date] = None
    type: TransactionType

    class Config:
        from_attributes = True
