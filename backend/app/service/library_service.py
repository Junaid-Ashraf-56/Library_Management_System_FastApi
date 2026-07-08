from __future__ import annotations

from datetime import UTC, datetime, timedelta
from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError

from app.repository.database import SessionLocal
from app.repository import library_repository as repository
from app.auth import  password as password_auth

class LibraryError(Exception):
    pass


class NotFoundError(LibraryError):
    pass


class ValidationError(LibraryError):
    pass


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
        raise HTTPException(status_code=400,detail="Stock cannot be negative.")
    if price < 0:
        raise HTTPException(status_code=400,detail="Price cannot be negative.")

    db = SessionLocal()
    try:
        book = repository.add_book(
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


def list_books():
    db = SessionLocal()
    try:
        return repository.list_books(db)
    finally:
        db.close()


def search_books(query: str):
    db = SessionLocal()
    try:
        return repository.search_books(db, query)
    finally:
        db.close()


def remove_book(book_id: int) -> None:
    db = SessionLocal()
    try:
        removed = repository.remove_book(db, book_id)

        if not removed:
            raise HTTPException(status_code=404,detail=f"No book exists with id {book_id}.")

        db.commit()

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot remove a book that is referenced by loan history."
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def register_user(
    *,
    name: str,
    email: str,
    phone_number: str,
    password: str,
):
    db = SessionLocal()
    try:
        user = repository.register_user(
            db,
            name=name,
            email=email,
            phone_number=phone_number,
            password=password_auth.hash_password(password)
        )

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"A user already uses {email}."
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def loan_book(
    *,
    book_id: int,
    member_id: int,
    days: int,
):
    if days < 1:
        raise HTTPException(status_code=400, detail="Loan length must be at least one day.")

    db = SessionLocal()
    try:
        book = repository.get_book_for_update(db, book_id)

        if book is None:
            raise HTTPException(status_code=404,detail=f"No book exists with id {book_id}.")

        if book.stock <= 0:
            raise HTTPException(status_code=404,detail=f"'{book.title}' is currently out of stock.")

        member = repository.get_member(db, member_id)

        if member is None:
            raise HTTPException(status_code=404,detail=f"No user exists with id {member_id}.")
        
        due_date = datetime.now(UTC) + timedelta(days=days)

        repository.decrease_stock(db, book_id)

        loan = repository.create_loan(
            db,
            book_id=book_id,
            member_id=member_id,
            due_date=due_date,
        )

        db.commit()
        db.refresh(loan)

        return loan

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def return_book(loan_id: int):
    db = SessionLocal()
    try:
        loan = repository.get_active_loan_for_update(db, loan_id)

        if loan is None:
            raise HTTPException(status_code=404,detail=f"No active loan exists with id {loan_id}.")

        returned_at = datetime.now(UTC)

        returned_loan = repository.mark_loan_returned(
            db,
            loan_id=loan_id,
            returned_at=returned_at,
        )

        book_id = int(loan.book_id)
        repository.increase_stock(db, book_id)

        db.commit()
        db.refresh(returned_loan)

        return returned_loan

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def list_loans(*, active_only: bool = False):
    db = SessionLocal()
    try:
        return repository.list_loans(db, active_only=active_only)
    finally:
        db.close()