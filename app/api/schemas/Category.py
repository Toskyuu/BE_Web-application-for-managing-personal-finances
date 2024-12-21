from typing import Optional

from pydantic import BaseModel, field_validator


class CategoryBase(BaseModel):
    name: str
    description: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryList(BaseModel):
    page: Optional[int] = 1
    size: Optional[int] = 10
    sort_by: Optional[str] = "id"
    order: Optional[str] = "asc"

    @field_validator("page")
    def validate_page(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Page number must be greater than 0")
        return value

    @field_validator("size")
    def validate_size(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Size must be at least 1")
        return value

    @field_validator("order")
    def validate_order(cls, value):
        if value and value not in ["asc", "desc"]:
            raise ValueError("Sort must be either asc or desc")
        return value

    @field_validator("sort_by")
    def validate_sort_by(cls, value):
        if value and value not in ["id", "name"]:
            raise ValueError("You can only sort by id or name")
        return value


class Category(BaseModel):
    id: int
    name: str
    description: str
    user_id: int
    deleted: Optional[bool] = False

    class Config:
        from_attributes = True
