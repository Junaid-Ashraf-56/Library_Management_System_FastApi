from datetime import datetime

from sqlalchemy.orm import Session

from app.model.book import Book
from app.model.enums import LoanStatus
from app.model.loan import Loan
from app.model.user import User


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


def get_active_loan_for_update(db: Session, loan_id: int) -> Loan | None:
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
) -> Loan | None:
    loan = db.get(Loan, loan_id)
    if loan is None:
        return None

    loan.status = LoanStatus.RETURNED
    loan.returned_at = returned_at
    db.flush()
    db.refresh(loan)
    return loan


def list_loans(
    db: Session,
    *,
    active_only: bool = False,
    member_id: int | None = None,
) -> list[Loan]:
    query = db.query(Loan).join(Book).join(User)

    if active_only:
        query = query.filter(Loan.status == LoanStatus.BORROWED)

    if member_id is not None:
        query = query.filter(Loan.member_id == member_id)

    return query.order_by(Loan.loan_id).all()
