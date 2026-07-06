from enum import Enum

class UserRole(Enum):
    MEMBER = "MEMBER"
    LIBRARIAN = "LIBRARIAN"


class LoanStatus(Enum):
    BORROWED = "BORROWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"