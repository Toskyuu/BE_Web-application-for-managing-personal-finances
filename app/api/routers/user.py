from app.api.schemas.User import UserCreate, User as UserSchema, UserUpdatePassword, User
from app.database.models.user import User as UserModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.services.auth import verify_password, create_access_token, get_password_hash
from app.database.repositories.user import UserRepository
from fastapi.security import OAuth2PasswordRequestForm

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@user_router.post("/auth/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email już używany")

    new_user = UserRepository.create_user(db, user.username, user.email, user.password)
    return new_user


@user_router.post("/auth/login")
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = UserRepository.get_user_by_email(db, user.username)  # 'username' w formularzu OAuth2 to email
    if db_user is None:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Złe hasło")

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not UserRepository.delete_user(db, user_id):
        raise HTTPException(status_code=500, detail="Failed to delete user")
    return {"message": "User deleted successfully"}


@user_router.put("/auth/change-password")
def change_password(user_id: int, password_data: UserUpdatePassword, db: Session = Depends(get_db)):
    user = UserRepository.get_user_by_id(db, user_id)
    if not user or not verify_password(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")

    hashed_new_password = get_password_hash(password_data.new_password)
    UserRepository.update_password(db, user_id, hashed_new_password)

    return {"message": "Password updated successfully"}


@user_router.get("/", response_model=list[User])
def list_users(db: Session = Depends(get_db)):
    return UserRepository.get_users(db)


@user_router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserRepository.get_user_by_id(db, user_id, )
