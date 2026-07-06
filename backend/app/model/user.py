from dataclasses import dataclass
from enums import UserRole

@dataclass
class User:
    user_id: int
    name: str
    email: str
    phone_number: str
    password: str
    role: UserRole