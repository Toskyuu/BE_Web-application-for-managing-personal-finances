from app.api.schemas.User import UserCreate, User as UserSchema
from app.database.models.user import User as UserModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.services.auth import verify_password, create_access_token
from app.database.repositories.user import UserRepository
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email już używany")

    new_user = UserRepository.create_user(db, user.username, user.email, user.password)
    return new_user


@router.post("/login")
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = UserRepository.get_user_by_email(db, user.username)  # 'username' w formularzu OAuth2 to email
    if db_user is None:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Złe hasło")

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
