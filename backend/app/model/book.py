from dataclasses import dataclass

@dataclass
class Book:
    book_id: int
    title: str
    author: str
    category: str
    price: float
    publish_year: int
    stock: int

