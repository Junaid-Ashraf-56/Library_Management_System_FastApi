from __future__ import annotations

import sys
from decimal import Decimal, InvalidOperation
from typing import Any

from app.repository.database import init_db
from app.service import LibraryError, book_service, loan_service, user_service


def _input_decimal(prompt: str) -> Decimal:
    while True:
        value = input(prompt).strip()
        try:
            return Decimal(value)
        except InvalidOperation:
            print("Please enter a valid number.")


def _input_int(prompt: str) -> int:
    while True:
        value = input(prompt).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid integer.")


def _to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row

    return {
        column.name: getattr(row, column.name)
        for column in row.__table__.columns
    }


def _print_rows(rows: list[Any]) -> None:
    if not rows:
        print("\nNo records found.\n")
        return

    dict_rows = [_to_dict(row) for row in rows]
    headers = list(dict_rows[0].keys())

    rendered_rows = [
        ["" if row[column] is None else str(row[column]) for column in headers]
        for row in dict_rows
    ]

    widths = [
        max(len(header), *(len(row[index]) for row in rendered_rows))
        for index, header in enumerate(headers)
    ]

    print()
    print(" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))

    for row in rendered_rows:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))

    print()


def show_menu() -> None:
    print("""
=========================================
        Library Management System
=========================================

1. Add Book
2. List Books
3. Search Books
4. Remove Book
5. Register Member
6. Loan Book
7. Return Book
8. List Loans
9. List Active Loans
0. Exit
""")


def add_book_menu() -> None:
    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()
    category = input("Enter category: ").strip()
    price = _input_int("Enter price: ")
    publish_year = _input_int("Enter publish year: ")
    stock = _input_int("Enter stock: ")

    book = book_service.add_book(
        title=title,
        author=author,
        category=category,
        price=price,
        publish_year=publish_year,
        stock=stock,
    )

    print("\nBook added successfully.")
    _print_rows([book])


def list_books_menu() -> None:
    _print_rows(book_service.list_books())


def search_books_menu() -> None:
    query = input("Enter search keyword: ").strip()
    _print_rows(book_service.search_books(query))


def remove_book_menu() -> None:
    book_id = _input_int("Enter book id: ")
    book_service.remove_book(book_id)
    print(f"\nBook {book_id} removed successfully.\n")


def register_member_menu() -> None:
    name = input("Enter member name: ").strip()
    email = input("Enter email: ").strip()
    phone = input("Enter phone number: ").strip()
    password = input("Enter password: ").strip()

    member = user_service.register_user(
        name=name,
        email=email,
        phone_number=phone,
        password=password,
    )

    print("\nMember registered successfully.")
    _print_rows([member])


def loan_book_menu() -> None:
    book_id = _input_int("Enter book id: ")
    member_id = _input_int("Enter member id: ")
    days = _input_int("Enter loan days: ")

    loan = loan_service.loan_book(
        book_id=book_id,
        member_id=member_id,
        days=days,
    )

    print("\nBook loan recorded successfully.")
    _print_rows([loan])


def return_book_menu() -> None:
    loan_id = _input_int("Enter loan id: ")

    loan = loan_service.return_book(loan_id)

    print("\nBook returned successfully.")
    _print_rows([loan])


def list_loans_menu(active_only: bool = False) -> None:
    _print_rows(loan_service.list_loans(active_only=active_only))


def main() -> int:
    init_db()
    while True:
        show_menu()
        choice = input("Select an option: ").strip()

        try:
            match choice:
                case "1":
                    add_book_menu()
                case "2":
                    list_books_menu()
                case "3":
                    search_books_menu()
                case "4":
                    remove_book_menu()
                case "5":
                    register_member_menu()
                case "6":
                    loan_book_menu()
                case "7":
                    return_book_menu()
                case "8":
                    list_loans_menu()
                case "9":
                    list_loans_menu(active_only=True)
                case "0":
                    print("\nGoodbye.\n")
                    return 0
                case _:
                    print("\nInvalid option. Please try again.\n")

        except LibraryError as exc:
            print(f"\nError: {exc}\n", file=sys.stderr)

        except Exception as exc:
            print(f"\nUnexpected error: {exc}\n", file=sys.stderr)



if __name__ == "__main__":
    raise SystemExit(main())
