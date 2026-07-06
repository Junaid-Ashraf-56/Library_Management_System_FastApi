from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.database import Base
from app.model.enums import UserRole


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(255))

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole)
    )