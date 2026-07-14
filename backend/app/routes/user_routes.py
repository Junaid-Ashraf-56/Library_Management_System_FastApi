from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt_auth import get_current_user, get_optional_current_user
from app.model.enums import UserRole
from app.model.user import User
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserRead
from app.service import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_data: UserCreate):
    return user_service.register_user(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password=user_data.password,
    )


@router.post(
    "/register-librarian",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_librarian(
    user_data: UserCreate,
    current_user: User | None = Depends(get_optional_current_user),
):
    if user_service.has_librarians():
        if current_user is None or current_user.role != UserRole.LIBRARIAN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="An existing librarian token is required.",
            )

    return user_service.register_librarian(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password=user_data.password,
    )


@router.post("/login", response_model=TokenResponse)
def login_user(credentials: LoginRequest):
    return user_service.login_user(
        email=credentials.email,
        password=credentials.password,
    )


@router.post("/librarian/login", response_model=TokenResponse)
def login_librarian(credentials: LoginRequest):
    return user_service.login_user(
        email=credentials.email,
        password=credentials.password,
        required_role=UserRole.LIBRARIAN,
    )


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
