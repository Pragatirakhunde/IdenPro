from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

class AuthService:
    """
    Handles all authentication-related business logic.
    """

    @staticmethod
    def get_user_by_username(
        db: Session,
        username: str
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def register_user(
        db: Session,
        user_data: UserCreate
    ) -> User:

        # Check username
        existing_user = (
            db.query(User)
            .filter(
                or_(
                    User.username == user_data.username,
                    User.email == user_data.email
                )
            )
            .first()
        )

        if existing_user:

            if existing_user.username == user_data.username:
                raise ValueError(
                    "Username already exists."
                )

            if existing_user.email == user_data.email:
                raise ValueError(
                    "Email already exists."
                )

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(
                user_data.password
            )
        )

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        return new_user

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> User | None:

        user = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.password_hash
        ):
            return None

        return user

    @staticmethod
    def login_user(
        db: Session,
        username: str,
        password: str
    ) -> dict:

        user = AuthService.authenticate_user(
            db,
            username,
            password
        )

        if not user:
            raise ValueError(
                "Invalid username or password."
            )

        access_token = create_access_token(
            {
                "sub": user.username
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }