from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres_utils import get_db
from app.api.schemas.Category import CategoryUpdate, CategoryCreate, Category, CategoryList
from app.database.repositories.category import CategoryRepository
from app.exceptions.category_exceptions import CategoryCreationError, CategoryUserNotFoundError, CategoryNotFoundError, \
    CategoryUpdateError, CategoryDeleteError

category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@category_router.post("/categories", response_model=list[Category])
async def list_categories(
        user_id: int,
        category: CategoryList,
        db: AsyncSession = Depends(get_db)):
    try:
        return await CategoryRepository.get_categories_by_user(
            db, user_id=user_id, page=category.page, size=category.size, sort_by=category.sort_by, order=category.order)
    except CategoryUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@category_router.get("/{category_id}", response_model=Category)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await CategoryRepository.get_category(db, category_id=category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@category_router.post("/", response_model=Category)
async def create_category(category: CategoryCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await CategoryRepository.create_category(db, category=category, user_id=user_id)
    except CategoryCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except CategoryUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@category_router.put("/{category_id}")
async def update_category(category_id: int, category_update: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    try:
        updated_category = await CategoryRepository.update_category(db, category_id, category_update)
        return updated_category
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CategoryUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))


@category_router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await CategoryRepository.delete_category(db, category_id)
        return {"message": "Category deleted successfully"}
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CategoryDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
