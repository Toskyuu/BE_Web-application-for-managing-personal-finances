from pydantic import BaseModel
from typing import Optional
from app.database.models.enums import AccountType


class AccountBase(BaseModel):
    name: str
    initial_balance: Optional[float] = 0.0
    type: AccountType


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    initial_balance: Optional[float] = None
    type: Optional[AccountType] = None


class Account(BaseModel):
    account_id: int
    user_id: int
    balance: Optional[float] = None
    type: AccountType
    initial_balance: Optional[float] = None
    deleted: Optional[bool] = False

    class Config:
        from_attributes = True
