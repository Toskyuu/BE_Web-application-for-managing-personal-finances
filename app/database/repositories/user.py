from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.services.auth import get_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class UserRepository:
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        try:
            with db.begin():
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")

                db.delete(user)
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error deleting user: " + str(e))

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> User:
        existing_user = db.query(User).filter((User.email == email)).first()
        if existing_user:
            raise ValueError("Użytkownik o podanym email już istnieje.")

        hashed_password = get_password_hash(password)
        db_user = User(username=username, email=email, password=hashed_password)
        db.add(db_user)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Wystąpił problem z zapisem użytkownika.")

        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_users(db: Session) -> list[User]:
        return db.query(User).all()

    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str):
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.password = new_password
            db.commit()
            db.refresh(user)
