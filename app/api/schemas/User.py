from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
    email: EmailStr


class User(UserBase):
    user_id: int
    is_mail_verified: bool

    class Config:
        from_attributes = True
