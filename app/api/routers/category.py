from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.Category import CategoryUpdate, CategoryCreate, Category
from app.database.repositories.category import CategoryRepository
from app.exceptions.category_exceptions import CategoryCreationError, CategoryUserNotFoundError, CategoryNotFoundError, \
    CategoryUpdateError, CategoryDeleteError

category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@category_router.get("/", response_model=list[Category])
def list_categories(user_id: int, db: Session = Depends(get_db)):
    try:
        return CategoryRepository.get_categories_by_user(db, user_id=user_id)
    except CategoryUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@category_router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    try:
        return CategoryRepository.get_category(db, category_id=category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@category_router.post("/", response_model=Category)
def create_category(category: CategoryCreate, user_id: int, db: Session = Depends(get_db)):
    try:
        return CategoryRepository.create_category(db, category=category, user_id=user_id)
    except CategoryCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except CategoryUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@category_router.put("/{category_id}")
def update_category(category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_db)):
    try:
        updated_category = CategoryRepository.update_category(db, category_id, category_update)
        return updated_category
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CategoryUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))


@category_router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        CategoryRepository.delete_category(db, category_id)
        return {"message": "Category deleted successfully"}
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CategoryDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
