from typing import Optional

from pydantic import BaseModel, field_validator

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


class AccountList(BaseModel):
    page: Optional[int] = 0
    size: Optional[int] = 0
    sort_by: Optional[str] = "id"
    order: Optional[str] = "asc"

    @field_validator("page")
    def validate_page(cls, value):
        if value is not None and value < 0:
            raise ValueError("Page number must be greater than 0")
        return value

    @field_validator("size")
    def validate_size(cls, value):
        if value is not None and value < 0:
            raise ValueError("Size must be at least 1")
        return value

    @field_validator("order")
    def validate_order(cls, value):
        if value and value not in ["asc", "desc"]:
            raise ValueError("Sort must be either asc or desc")
        return value

    @field_validator("sort_by")
    def validate_sort_by(cls, value):
        if value and value not in ["id", "balance", "initial_balance", "type", "name"]:
            raise ValueError("You can only sort by id, name, balance, initial balance or type")
        return value


class Account(BaseModel):
    id: int
    name: str
    user_id: int
    balance: Optional[float] = None
    type: AccountType
    initial_balance: Optional[float] = None
    deleted: Optional[bool] = False

    class Config:
        from_attributes = True
