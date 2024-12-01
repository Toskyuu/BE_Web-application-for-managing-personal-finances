from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.Category import CategoryUpdate, CategoryCreate, Category
from app.database.repositories.category import CategoryRepository

category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@category_router.get("/", response_model=list[Category])
def list_categories(user_id: int, db: Session = Depends(get_db)):
    return CategoryRepository.get_categories_by_user(db, user_id=user_id)


@category_router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = CategoryRepository.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@category_router.post("/", response_model=Category)
def create_category(category: CategoryCreate, user_id: int, db: Session = Depends(get_db)):
    return CategoryRepository.create_category(db, category=category, user_id=user_id)


@category_router.put("/{category_id}")
async def update_category(category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_db)):
    updated_category = CategoryRepository.update_category(db, category_id, category_update)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category


@category_router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    success = CategoryRepository.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
