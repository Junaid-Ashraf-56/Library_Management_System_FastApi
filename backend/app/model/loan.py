from datetime import datetime
from sqlalchemy import func
from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repository.database import Base
from app.model.enums import LoanStatus


class Loan(Base):
    __tablename__ = "loans"

    loan_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.book_id")
    )

    member_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id")
    )

    issue_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    due_date: Mapped[datetime] = mapped_column(DateTime)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime)

    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus)
    )

    book = relationship("Book")
    member = relationship("User")