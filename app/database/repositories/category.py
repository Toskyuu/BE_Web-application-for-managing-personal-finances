from sqlalchemy.orm import Session
from app.database.models.category import Category
from app.api.schemas.Category import CategoryUpdate, CategoryCreate


class CategoryRepository:
    @staticmethod
    def get_category(db: Session, category_id: int):
        return db.query(Category).filter(
            Category.category_id == category_id,
            Category.deleted == False
        ).first()

    @staticmethod
    def get_categories_by_user(db: Session, user_id: int):
        return db.query(Category).filter(
            Category.user_id == user_id,
            Category.deleted == False
        ).all()

    @staticmethod
    def create_category(db: Session, category: CategoryCreate, user_id: int):

        db_category = Category(**category.model_dump(), user_id=user_id)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Category:
        category = db.query(Category).filter(Category.category_id == category_id).first()
        updated_category = category_update.model_dump(exclude_unset=True)
        for key, value in updated_category.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        category = db.query(Category).filter(Category.category_id == category_id).first()
        if category:
            category.deleted = True
            db.commit()
            return True
        return False
