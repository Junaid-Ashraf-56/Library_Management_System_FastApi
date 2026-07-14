from fastapi import APIRouter, Depends, Response, status

from app.auth.jwt_auth import get_current_librarian
from app.model.user import User
from app.schemas import BookCreate, BookRead, BookUpdate
from app.service import book_service

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookRead])
def list_books():
    return book_service.list_books()


@router.get("/search", response_model=list[BookRead])
def search_books(query: str):
    return book_service.search_books(query)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int):
    return book_service.get_book(book_id)


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def add_book(
    book_data: BookCreate,
    _current_librarian: User = Depends(get_current_librarian),
):
    return book_service.add_book(
        title=book_data.title,
        author=book_data.author,
        category=book_data.category,
        price=book_data.price,
        publish_year=book_data.publish_year,
        stock=book_data.stock,
    )


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    _current_librarian: User = Depends(get_current_librarian),
):
    return book_service.update_book(
        book_id,
        **book_data.model_dump(exclude_unset=True),
    )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(
    book_id: int,
    _current_librarian: User = Depends(get_current_librarian),
):
    book_service.remove_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
