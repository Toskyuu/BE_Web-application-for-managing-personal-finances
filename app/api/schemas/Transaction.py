from pydantic import BaseModel
from typing import Optional
from datetime import date


class TransactionBase(BaseModel):
    description: str
    amount: float
    date: Optional[date]


class TransactionCreate(TransactionBase):
    category_id: int
    account_id: int


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None


class Transaction(TransactionBase):
    description: str
    amount: float
    date: Optional[date]
    category_id: int
    account_id: int
    user_id: int
    transaction_id: int

    class Config:
        from_attributes = True
