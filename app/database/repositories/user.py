from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.exceptions.user_exceptions import UserDeleteError, UserNotFoundError, UserCreationError, \
    UserUpdatePasswordError, UserEmailExistError, UserInvalidPassword, UserEmailNotFoundError, UserLoginError, \
    UserLoginDataError
from app.services.auth import get_password_hash, verify_password, create_access_token


class UserRepository:

    @staticmethod
    def login(db: Session, email: str, password: str):
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not verify_password(password, user.password):
                raise UserLoginDataError()
            access_token = create_access_token(data={"sub": user.email})
            return {"access_token": access_token, "token_type": "bearer"}
        except SQLAlchemyError as e:
            raise UserLoginError(str(e))
        # except PyJWTError as e:
        #     raise UserLoginError(str(e))

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        try:
            with db.begin():
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    raise UserNotFoundError(user_id)
                db.delete(user)
            return True
        except SQLAlchemyError as e:
            raise UserDeleteError(str(e))

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> User:
        try:
            with db.begin():
                existing_user = db.query(User).filter(User.email == email).first()
                if existing_user:
                    raise UserEmailExistError(email)

                hashed_password = get_password_hash(password)
                db_user = User(username=username, email=email, password=hashed_password)

                db.add(db_user)

                return db_user

        except IntegrityError as e:
            raise UserCreationError(str(e))
        except SQLAlchemyError as e:
            raise UserCreationError(str(e))

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise UserEmailNotFoundError(email)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)
        return user

    @staticmethod
    def get_users(db: Session) -> list[User]:
        return db.query(User).all()

    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str, old_password: str):
        try:
            with db.begin():
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    raise UserNotFoundError(user_id)
                if not verify_password(old_password, user.password):
                    raise UserInvalidPassword()

                user.password = get_password_hash(new_password)
        except SQLAlchemyError as e:
            raise UserUpdatePasswordError(f"{user_id}: {str(e)}")
