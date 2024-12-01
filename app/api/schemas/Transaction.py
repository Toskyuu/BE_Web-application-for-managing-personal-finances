import datetime

from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.database.models.enums import TransactionType


class TransactionBase(BaseModel):
    description: Optional[str]
    amount: float
    date: Optional[date] = None


class TransactionCreate(TransactionBase):
    category_id: int
    account_id: int
    account_id_2: Optional[int] = None
    type: TransactionType


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    account_id_2: Optional[int] = None
    type: Optional[TransactionType] = None


class Transaction(TransactionBase):
    transaction_id: int
    category_id: int
    account_id: int
    account_id_2: Optional[int] = None
    user_id: int
    date: Optional[datetime.date] = None
    type: TransactionType

    class Config:
        from_attributes = True
