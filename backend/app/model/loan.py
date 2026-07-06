from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enums import LoanStatus
@dataclass
class Loan:
    loan_id: int
    book_id: int
    member_id: int
    issue_date: datetime
    due_date: datetime
    returned_at: Optional[datetime]
    status: LoanStatus