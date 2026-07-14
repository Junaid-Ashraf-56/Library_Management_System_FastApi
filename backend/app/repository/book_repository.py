from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.model.book import Book


def add_book(
    db: Session,
    *,
    title: str,
    author: str,
    category: str,
    price: float,
    publish_year: int,
    stock: int,
) -> Book:
    book = Book(
        title=title,
        author=author,
        category=category,
        price=price,
        publish_year=publish_year,
        stock=stock,
    )

    db.add(book)
    db.flush()
    db.refresh(book)
    return book


def list_books(db: Session) -> list[Book]:
    return db.query(Book).order_by(Book.book_id).all()


def get_book(db: Session, book_id: int) -> Book | None:
    return db.get(Book, book_id)


def search_books(db: Session, query: str) -> list[Book]:
    pattern = f"%{query}%"
    return (
        db.query(Book)
        .filter(
            or_(
                Book.title.ilike(pattern),
                Book.author.ilike(pattern),
                Book.category.ilike(pattern),
            )
        )
        .order_by(Book.book_id)
        .all()
    )


def remove_book(db: Session, book_id: int) -> bool:
    book = db.get(Book, book_id)
    if book is None:
        return False

    db.delete(book)
    db.flush()
    return True


def update_book(db: Session, book_id: int, **book_data) -> Book | None:
    book = db.get(Book, book_id)
    if book is None:
        return None

    for field, value in book_data.items():
        setattr(book, field, value)

    db.flush()
    db.refresh(book)
    return book


def get_book_for_update(db: Session, book_id: int) -> Book | None:
    return (
        db.query(Book)
        .filter(Book.book_id == book_id)
        .with_for_update()
        .first()
    )


def decrease_stock(db: Session, book_id: int) -> None:
    book = db.get(Book, book_id)
    if book is not None:
        book.stock -= 1
        db.flush()


def increase_stock(db: Session, book_id: int) -> None:
    book = db.get(Book, book_id)
    if book is not None:
        book.stock += 1
        db.flush()
