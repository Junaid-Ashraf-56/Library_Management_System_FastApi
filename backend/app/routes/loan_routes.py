from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt_auth import get_current_user
from app.model.enums import UserRole
from app.model.user import User
from app.schemas import LoanCreate, LoanRead
from app.service import loan_service

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
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

    return loan_service.loan_book(
        book_id=loan_data.book_id,
        member_id=member_id,
        days=loan_data.days,
    )


@router.post("/{loan_id}/return", response_model=LoanRead)
def return_book(
    loan_id: int,
    current_user: User = Depends(get_current_user),
):
    member_id = None
    if current_user.role != UserRole.LIBRARIAN:
        member_id = current_user.user_id

    return loan_service.return_book(loan_id, member_id=member_id)


@router.get("", response_model=list[LoanRead])
def list_loans(
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    member_id = None
    if current_user.role != UserRole.LIBRARIAN:
        member_id = current_user.user_id

    return loan_service.list_loans(
        active_only=active_only,
        member_id=member_id,
    )
