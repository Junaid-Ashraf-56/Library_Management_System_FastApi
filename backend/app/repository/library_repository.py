from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.model.book import Book
from app.model.user import User
from app.model.loan import Loan
from app.model.enums import UserRole, LoanStatus


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


def list_books(db: Session) -> list[type[Book]]:
    return db.query(Book).order_by(Book.book_id).all()


def search_books(db: Session, query: str) -> list[type[Book]]:
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


def get_book_for_update(db: Session, book_id: int) -> type[Book] | None:
    return (
        db.query(Book)
        .filter(Book.book_id == book_id)
        .with_for_update()
        .first()
    )


def register_user(
    db: Session,
    *,
    name: str,
    email: str,
    phone_number: str,
    password: str,
) -> User:
    user = User(
        name=name,
        email=email,
        phone_number=phone_number,
        password=password,
        role=UserRole.MEMBER,
    )

    db.add(user)
    db.flush()
    db.refresh(user)

    return user


def get_member(db: Session, member_id: int) -> type[User] | None:
    return db.get(User, member_id)


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


def create_loan(
    db: Session,
    *,
    book_id: int,
    member_id: int,
    due_date: datetime,
) -> Loan:
    loan = Loan(
        book_id=book_id,
        member_id=member_id,
        due_date=due_date,
        status=LoanStatus.BORROWED,
    )

    db.add(loan)
    db.flush()
    db.refresh(loan)

    return loan


def get_active_loan_for_update(
    db: Session,
    loan_id: int,
) -> type[Loan] | None:
    return (
        db.query(Loan)
        .filter(
            Loan.loan_id == loan_id,
            Loan.status == LoanStatus.BORROWED,
        )
        .with_for_update()
        .first()
    )


def mark_loan_returned(
    db: Session,
    *,
    loan_id: int,
    returned_at: datetime,
) -> type[Loan] | None:
    loan = db.get(Loan, loan_id)

    if loan is None:
        return None

    loan.status = LoanStatus.RETURNED
    loan.returned_at = returned_at

    db.flush()
    db.refresh(loan)

    return loan


def list_loans(db: Session, *, active_only: bool = False) -> list[type[Loan]]:
    query = db.query(Loan).join(Book).join(User)

    if active_only:
        query = query.filter(Loan.status == LoanStatus.BORROWED)

    return query.order_by(Loan.loan_id).all()