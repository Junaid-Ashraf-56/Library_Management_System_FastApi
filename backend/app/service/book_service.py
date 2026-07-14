from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.repository import book_repository
from app.repository.database import SessionLocal


def add_book(
    *,
    title: str,
    author: str,
    category: str,
    price: float,
    publish_year: int,
    stock: int,
):
    if stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative.")
    if price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative.")

    db = SessionLocal()
    try:
        book = book_repository.add_book(
            db,
            title=title,
            author=author,
            category=category,
            price=price,
            publish_year=publish_year,
            stock=stock,
        )
        db.commit()
        db.refresh(book)
        return book
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_book(book_id: int):
    db = SessionLocal()
    try:
        book = book_repository.get_book(db, book_id)
        if book is None:
            raise HTTPException(
                status_code=404,
                detail=f"No book exists with id {book_id}.",
            )
        return book
    finally:
        db.close()


def list_books():
    db = SessionLocal()
    try:
        return book_repository.list_books(db)
    finally:
        db.close()


def search_books(query: str):
    db = SessionLocal()
    try:
        return book_repository.search_books(db, query)
    finally:
        db.close()


def remove_book(book_id: int) -> None:
    db = SessionLocal()
    try:
        removed = book_repository.remove_book(db, book_id)
        if not removed:
            raise HTTPException(
                status_code=404,
                detail=f"No book exists with id {book_id}.",
            )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot remove a book that is referenced by loan history.",
        ) from exc
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_book(book_id: int, **book_data):
    if "stock" in book_data and book_data["stock"] is not None:
        if book_data["stock"] < 0:
            raise HTTPException(status_code=400, detail="Stock cannot be negative.")
    if "price" in book_data and book_data["price"] is not None:
        if book_data["price"] < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative.")

    clean_data = {key: value for key, value in book_data.items() if value is not None}
    if not clean_data:
        raise HTTPException(status_code=400, detail="No book fields were provided.")

    db = SessionLocal()
    try:
        book = book_repository.update_book(db, book_id, **clean_data)
        if book is None:
            raise HTTPException(
                status_code=404,
                detail=f"No book exists with id {book_id}.",
            )
        db.commit()
        db.refresh(book)
        return book
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
