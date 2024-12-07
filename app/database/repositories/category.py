from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.models.category import Category
from app.api.schemas.Category import CategoryUpdate, CategoryCreate
from app.database.models.user import User
from app.exceptions.category_exceptions import CategoryNotFoundError, CategoryUserNotFoundError, CategoryCreationError, \
    CategoryUpdateError, CategoryDeleteError


class CategoryRepository:
    @staticmethod
    def get_category(db: Session, category_id: int):
        category = db.query(Category).filter(
            Category.category_id == category_id,
            Category.deleted == False
        ).first()
        if not category:
            raise CategoryNotFoundError
        return category

    @staticmethod
    def get_categories_by_user(db: Session, user_id: int):
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise CategoryUserNotFoundError(user_id)
        return db.query(Category).filter(
            Category.user_id == user_id,
            Category.deleted == False
        ).all()

    @staticmethod
    def create_category(db: Session, category: CategoryCreate, user_id: int):
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise CategoryUserNotFoundError(user_id)
            db_category = Category(**category.model_dump(), user_id=user_id)
            db.add(db_category)
            db.commit()
            db.refresh(db_category)
            return db_category
        except SQLAlchemyError as e:
            raise CategoryCreationError(str(e))

    @staticmethod
    def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Category:
        try:
            with db.begin():
                category = db.query(Category).filter(Category.category_id == category_id).first()
                if not category:
                    raise CategoryNotFoundError
                updated_category = category_update.model_dump(exclude_unset=True)
                for key, value in updated_category.items():
                    setattr(category, key, value)

                db.refresh(category)
                return category
        except SQLAlchemyError as e:
            raise CategoryUpdateError(str(e))

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        try:
            with db.begin():
                category = db.query(Category).filter(Category.category_id == category_id).first()
                if not category:
                    raise CategoryNotFoundError

                category.deleted = True
                db.refresh(category)
                return True
        except SQLAlchemyError as e:
            raise CategoryDeleteError(str(e))
