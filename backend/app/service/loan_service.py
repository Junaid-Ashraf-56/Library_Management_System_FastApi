from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from app.repository import book_repository, loan_repository, user_repository
from app.repository.database import SessionLocal


def loan_book(*, book_id: int, member_id: int, days: int):
    if days < 1:
        raise HTTPException(status_code=400, detail="Loan length must be at least one day.")

    db = SessionLocal()
    try:
        book = book_repository.get_book_for_update(db, book_id)
        if book is None:
            raise HTTPException(
                status_code=404,
                detail=f"No book exists with id {book_id}.",
            )
        if book.stock <= 0:
            raise HTTPException(
                status_code=404,
                detail=f"'{book.title}' is currently out of stock.",
            )

        member = user_repository.get_member(db, member_id)
        if member is None:
            raise HTTPException(
                status_code=404,
                detail=f"No user exists with id {member_id}.",
            )

        due_date = datetime.now(UTC) + timedelta(days=days)
        book_repository.decrease_stock(db, book_id)
        loan = loan_repository.create_loan(
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
        loan = loan_repository.get_active_loan_for_update(db, loan_id)
        if loan is None:
            raise HTTPException(
                status_code=404,
                detail=f"No active loan exists with id {loan_id}.",
            )
        if member_id is not None and loan.member_id != member_id:
            raise HTTPException(
                status_code=403,
                detail="You can only return your own loans.",
            )

        returned_loan = loan_repository.mark_loan_returned(
            db,
            loan_id=loan_id,
            returned_at=datetime.now(UTC),
        )
        book_repository.increase_stock(db, int(loan.book_id))

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
        loans = loan_repository.list_loans(
            db,
            active_only=active_only,
            member_id=member_id,
        )
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
