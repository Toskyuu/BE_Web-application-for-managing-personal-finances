from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.database.repositories.user import create_user
from app.api.schemas.User import UserCreate, User

router = APIRouter()


@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email już używany")

    new_user = create_user(db, user.email, user.password)
    return new_user
