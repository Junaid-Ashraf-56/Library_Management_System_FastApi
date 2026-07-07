from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.repository.database import Base


class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    publish_year: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer)