from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.enums import UserRole
from app.model.user import User


def register_user(
    db: Session,
    *,
    name: str,
    email: str,
    phone_number: str,
    password: str,
    role: UserRole = UserRole.MEMBER,
) -> User:
    user = User(
        name=name,
        email=email,
        phone_number=phone_number,
        password=password,
        role=role,
    )

    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def count_librarians(db: Session) -> int:
    return db.query(User).filter(User.role == UserRole.LIBRARIAN).count()


def get_member(db: Session, member_id: int) -> User | None:
    return db.get(User, member_id)
