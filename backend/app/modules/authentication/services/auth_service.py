from datetime import timedelta

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.authentication.models.user import User
from app.modules.authentication.schemas.user import Token, UserCreate, UserLogin


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email is already registered.")

        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )

        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            raise ValueError("Email is already registered.")
        except OperationalError:
            db.rollback()
            raise

        return new_user

    @staticmethod
    def login_user(db: Session, credentials: UserLogin) -> Token:
        try:
            user = db.query(User).filter(User.email == credentials.email).first()
        except OperationalError:
            raise

        if user is None or not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Invalid credentials")

        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")
