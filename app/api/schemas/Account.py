from pydantic import BaseModel
from typing import Optional
from app.database.models.enums import AccountType


class AccountBase(BaseModel):
    name: str
    initial_balance: Optional[float] = 0.0
    type: AccountType


class AccountCreate(AccountBase):
    pass


class AccountNameUpdate(BaseModel):
    name: str


class AccountInitialBalanceUpdate(BaseModel):
    initial_balance: float


class AccountTypeUpdate(BaseModel):
    type: AccountType


class Account(AccountBase):
    account_id: int
    user_id: int
    balance: Optional[float] = None
    type: AccountType
    initial_balance: Optional[float] = None

    class Config:
        from_attributes = True
