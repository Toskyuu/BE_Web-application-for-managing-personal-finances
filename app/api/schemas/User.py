import re
from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(schemas.BaseUserCreate):
    username: str

    @field_validator("password")
    def validate_password(cls, value):
        password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"
        if not re.match(password_regex, value):
            raise ValueError(
                "Password must be at least 8 characters long, include a lowercase letter, an uppercase letter, a digit, and a special character.")
        return value

    @field_validator("username")
    def validate_username(cls, value):
        if not (3 <= len(value) <= 30):
            raise ValueError("Username must be between 3 and 30 characters.")
        return value


class UserRead(schemas.BaseUser[int]):
    id: int


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("username")
    def validate_username(cls, value):
        if not (3 <= len(value) <= 30):
            raise ValueError("Username must be between 3 and 30 characters.")
        return value


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    id: int
    is_verified: bool

    class Config:
        from_attributes = True
