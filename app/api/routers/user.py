from app.api.schemas.User import UserCreate, User as UserSchema, UserUpdatePassword, User
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.exceptions.user_exceptions import UserEmailExistError, UserCreationError, UserNotFoundError, UserDeleteError, \
    UserLoginError, UserLoginDataError, UserUpdatePasswordError, UserInvalidPassword, UserEmailNotFoundError
from app.database.repositories.user import UserRepository
from fastapi.security import OAuth2PasswordRequestForm

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@user_router.get("/email", response_model=User)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    try:
        return UserRepository.get_user_by_email(db, email)
    except UserEmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_router.post("/auth/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = UserRepository.create_user(db, user.username, user.email, user.password)
        return new_user
    except UserEmailExistError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/auth/login")
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        login_data = UserRepository.login(db, user.username, user.password)
        return login_data
    except UserLoginError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UserLoginDataError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@user_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        UserRepository.delete_user(db, user_id)
        return {"message": "User deleted successfully"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.put("/auth/change-password")
def change_password(user_id: int, password_data: UserUpdatePassword, db: Session = Depends(get_db)):
    try:
        UserRepository.update_password(db, user_id, password_data.password, password_data.old_password)
        return {"message": "Password updated successfully"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserInvalidPassword as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserUpdatePasswordError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@user_router.get("/", response_model=list[User])
def list_users(db: Session = Depends(get_db)):
    return UserRepository.get_users(db)


@user_router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return UserRepository.get_user_by_id(db, user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
