from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth.jwt_auth import get_current_user, get_optional_current_user
from app.model.enums import UserRole
from app.model.user import User
from app.schemas import (
    BookCreate,
    BookRead,
    BookUpdate,
    LoanCreate,
    LoanRead,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.service import library_service

router = APIRouter()


def require_librarian(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.LIBRARIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Librarian privileges required",
        )

    return current_user


@router.post(
    "/auth/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
)
def register_user(user_data: UserCreate):
    return library_service.register_user(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password=user_data.password,
    )


@router.post(
    "/auth/register-librarian",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
)
def register_librarian(
    user_data: UserCreate,
    current_user: User | None = Depends(get_optional_current_user),
):
    if library_service.has_librarians():
        if current_user is None or current_user.role != UserRole.LIBRARIAN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="An existing librarian token is required.",
            )

    return library_service.register_librarian(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password=user_data.password,
    )


@router.post(
            "/auth/login",
             response_model=TokenResponse,
             tags=["Auth"]
)
def login_user(credentials: LoginRequest):
    return library_service.login_user(
        email=credentials.email,
        password=credentials.password,
    )


@router.get(
    "/books",
    response_model=list[BookRead],
    tags=["Books"]
)
def list_books():
    return library_service.list_books()


@router.get(
    "/books/search",
    response_model=list[BookRead],
    tags=["Books"]
)
def search_books(query: str):
    return library_service.search_books(query)


@router.get(
    "/books/{book_id}",
    response_model=BookRead,
    tags=["Books"]
)
def get_book(book_id: int):
    return library_service.get_book(book_id)


@router.post(
    "/books",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
)
def add_book(
    book_data: BookCreate,
):
    return library_service.add_book(
        title=book_data.title,
        author=book_data.author,
        category=book_data.category,
        price=book_data.price,
        publish_year=book_data.publish_year,
        stock=book_data.stock,
    )


@router.patch(
    "/books/{book_id}",
    response_model=BookRead,
    tags=["Books"]
)
def update_book(
    book_id: int,
    book_data: BookUpdate,
):
    return library_service.update_book(
        book_id,
        **book_data.model_dump(exclude_unset=True),
    )


@router.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Books"],
)
def remove_book(
    book_id: int,
):
    library_service.remove_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/loans",
    response_model=LoanRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Loans"],
)
def loan_book(
    loan_data: LoanCreate,
    current_user: User = Depends(get_current_user),
):
    member_id = current_user.user_id

    if loan_data.member_id is not None:
        if current_user.role != UserRole.LIBRARIAN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only librarians can create loans for another member",
            )
        member_id = loan_data.member_id

    return library_service.loan_book(
        book_id=loan_data.book_id,
        member_id=member_id,
        days=loan_data.days,
    )


@router.post(
    "/loans/{loan_id}/return",
    response_model=LoanRead,
    tags=["Loans"]
)
def return_book(
    loan_id: int,
    current_user: User = Depends(get_current_user),
):
    member_id = None

    if current_user.role != UserRole.LIBRARIAN:
        member_id = current_user.user_id

    return library_service.return_book(loan_id, member_id=member_id)


@router.get(
    "/loans",
    response_model=list[LoanRead],
    tags=["Loans"]
)
def list_loans(
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    member_id = None

    if current_user.role != UserRole.LIBRARIAN:
        member_id = current_user.user_id

    return library_service.list_loans(
        active_only=active_only,
        member_id=member_id,
    )
