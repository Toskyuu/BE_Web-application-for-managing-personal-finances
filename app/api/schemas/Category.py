from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    name: str
    description: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Category(CategoryBase):
    category_id: int
    name: str
    description: str
    user_id: int
    deleted: Optional[bool] = False


    class Config:
        from_attributes = True
