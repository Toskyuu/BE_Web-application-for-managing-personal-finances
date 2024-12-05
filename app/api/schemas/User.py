import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="A valid email address.")
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"
        if not re.match(password_regex, value):
            raise ValueError(
                "Password must be at least 8 characters long, include a lowercase letter, an uppercase letter, a digit, and a special character.")
        return value


class UserCreate(UserBase):
    username: str

    @field_validator("username")
    def validate_username(cls, value):
        if not (3 <= len(value) <= 30):
            raise ValueError("Username must be between 3 and 30 characters.")
        return value


class UserLogin(BaseModel):
    password: str
    email: EmailStr = Field(..., description="A valid email address.")


class UserUpdatePassword(UserBase):
    old_password: str


class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    password: str
    is_mail_verified: bool

    class Config:
        from_attributes = True
