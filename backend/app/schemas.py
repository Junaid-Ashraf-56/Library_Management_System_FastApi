from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.model.enums import LoanStatus, UserRole


class UserCreate(BaseModel):
    name: str
    email: str
    phone_number: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    phone_number: str
    role: UserRole


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class BookBase(BaseModel):
    title: str
    author: str
    category: str
    price: float
    publish_year: int
    stock: int


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    category: str | None = None
    price: Decimal | None = None
    publish_year: int | None = None
    stock: int | None = None


class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)

    book_id: int


class LoanCreate(BaseModel):
    book_id: int
    days: int
    member_id: int | None = None


class LoanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loan_id: int
    book_id: int
    member_id: int
    issue_date: datetime
    due_date: datetime
    returned_at: datetime | None
    status: LoanStatus
    book: BookRead
    member: UserRead


class BorrowLoanResponse(BaseModel):
    loan: LoanRead
    job_id: str
    message: str


class ReturnLoanResponse(BaseModel):
    loan: LoanRead
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    task_status: str
    message: str
    pdf_download_url: str | None = None
