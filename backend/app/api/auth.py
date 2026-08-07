from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)
from app.schemas.auth import Token
from app.services.auth_service import AuthService
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """

    try:
        created_user = AuthService.register_user(
            db=db,
            user_data=user
        )

        return created_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=Token
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    """

    try:

        login_data = AuthService.login_user(
            db=db,
            username=user.username,
            password=user.password
        )

        return {
            "access_token": login_data["access_token"],
            "token_type": login_data["token_type"]
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Return currently logged-in user.
    """

    return current_user