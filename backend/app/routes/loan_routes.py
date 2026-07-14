from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt_auth import get_current_user
from app.core.celery_app import celery_app
from app.model.enums import UserRole
from app.model.user import User
from app.schemas import (
    BorrowLoanResponse,
    JobStatusResponse,
    LoanCreate,
    LoanRead,
    ReturnLoanResponse,
)
from app.service import loan_service
from app.tasks.receipt_tasks import generate_borrow_receipt

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post(
    "",
    response_model=BorrowLoanResponse,
    status_code=status.HTTP_201_CREATED,
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

    loan = loan_service.loan_book(
        book_id=loan_data.book_id,
        member_id=member_id,
        days=loan_data.days,
    )
    loan_snapshot = LoanRead.model_validate(loan).model_dump(mode="json")
    receipt_job = generate_borrow_receipt.delay(loan_snapshot)

    return {
        "loan": loan,
        "job_id": receipt_job.id,
        "message": "Receipt is being generated.",
    }


@router.post("/{loan_id}/return", response_model=ReturnLoanResponse)
def return_book(
    loan_id: int,
    current_user: User = Depends(get_current_user),
):
    member_id = None
    if current_user.role != UserRole.LIBRARIAN:
        member_id = current_user.user_id

    loan = loan_service.return_book(loan_id, member_id=member_id)
    return {"loan": loan, "message": "Book returned successfully."}


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


@router.get(
    "/receipt-jobs/{job_id}",
    response_model=JobStatusResponse,
)
def get_receipt_job_status(
    job_id: str,
    _current_user: User = Depends(get_current_user),
):
    job = AsyncResult(job_id, app=celery_app)

    if job.successful():
        result = job.result if isinstance(job.result, dict) else {}
        return {
            "job_id": job_id,
            "task_status": job.status,
            "message": result.get("message", "Receipt generated successfully."),
            "pdf_download_url": result.get("pdf_download_url"),
        }

    if job.failed():
        return {
            "job_id": job_id,
            "task_status": job.status,
            "message": "Receipt generation failed.",
        }

    messages = {
        "PENDING": "Receipt job is waiting to start.",
        "STARTED": "Receipt is being generated.",
        "RETRY": "Receipt generation is being retried.",
    }
    return {
        "job_id": job_id,
        "task_status": job.status,
        "message": messages.get(job.status, "Receipt job is in progress."),
    }
