from sqlalchemy.orm import Session
from app.database.models.user import User
from app.services.auth import get_password_hash
from sqlalchemy.exc import IntegrityError


def create_user(db: Session, username: str, email: str, password: str):
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
