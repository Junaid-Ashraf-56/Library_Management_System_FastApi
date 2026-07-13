from __future__ import annotations

from datetime import UTC, datetime, timedelta
from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError

from app.auth.jwt_auth import create_access_token
from app.repository.database import SessionLocal
from app.repository import library_repository as repository
from app.auth import  password as password_auth
from app.model.enums import UserRole

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


def get_book(book_id: int):
    db = SessionLocal()
    try:
        book = repository.get_book(db, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail=f"No book exists with id {book_id}.")

        return book
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


def update_book(book_id: int, **book_data):
    if "stock" in book_data and book_data["stock"] is not None and book_data["stock"] < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative.")
    if "price" in book_data and book_data["price"] is not None and book_data["price"] < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative.")

    clean_data = {
        key: value
        for key, value in book_data.items()
        if value is not None
    }

    if not clean_data:
        raise HTTPException(status_code=400, detail="No book fields were provided.")

    db = SessionLocal()
    try:
        book = repository.update_book(db, book_id, **clean_data)

        if book is None:
            raise HTTPException(status_code=404, detail=f"No book exists with id {book_id}.")

        db.commit()
        db.refresh(book)

        return book

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def login_user(*, email: str, password: str, required_role: UserRole | None = None):
    db = SessionLocal()
    try:
        user = repository.get_user_by_email(db, email)

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not password_auth.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if required_role is not None and user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="This account does not have librarian access.",
            )

        access_token = create_access_token({
            "sub": str(user.user_id),
            "role": user.role.value
        })

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

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


def register_librarian(
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
            password=password_auth.hash_password(password),
            role=UserRole.LIBRARIAN,
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


def has_librarians() -> bool:
    db = SessionLocal()
    try:
        return repository.count_librarians(db) > 0
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

        return _serialize_loan(loan)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def return_book(loan_id: int, *, member_id: int | None = None):
    db = SessionLocal()
    try:
        loan = repository.get_active_loan_for_update(db, loan_id)

        if loan is None:
            raise HTTPException(status_code=404,detail=f"No active loan exists with id {loan_id}.")

        if member_id is not None and loan.member_id != member_id:
            raise HTTPException(
                status_code=403,
                detail="You can only return your own loans.",
            )

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

        return _serialize_loan(returned_loan)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def list_loans(*, active_only: bool = False, member_id: int | None = None):
    db = SessionLocal()
    try:
        loans = repository.list_loans(db, active_only=active_only, member_id=member_id)
        return [_serialize_loan(loan) for loan in loans]
    finally:
        db.close()


def _serialize_loan(loan):
    return {
        "loan_id": loan.loan_id,
        "book_id": loan.book_id,
        "member_id": loan.member_id,
        "issue_date": loan.issue_date,
        "due_date": loan.due_date,
        "returned_at": loan.returned_at,
        "status": loan.status,
        "book": loan.book,
        "member": loan.member,
    }
