import os
from types import SimpleNamespace

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://library:library@localhost/library_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.main import app
from app.repository import book_repository, loan_repository, user_repository
from app.service import book_service, loan_service, user_service


def test_domain_modules_are_importable():
    assert callable(book_repository.get_book)
    assert callable(user_repository.get_user_by_email)
    assert callable(loan_repository.create_loan)
    assert callable(book_service.list_books)
    assert callable(user_service.register_user)
    assert callable(loan_service.loan_book)


def test_existing_api_paths_are_preserved():
    paths = set(app.openapi()["paths"])
    expected_paths = {
        "/auth/register",
        "/auth/register-librarian",
        "/auth/login",
        "/auth/librarian/login",
        "/auth/me",
        "/books",
        "/books/search",
        "/books/{book_id}",
        "/loans",
        "/loans/receipt-jobs/{job_id}",
        "/loans/{loan_id}/return",
    }

    assert expected_paths <= paths


def test_borrow_keeps_stock_and_loan_in_one_transaction(monkeypatch):
    events = []

    class FakeSession:
        def commit(self):
            events.append("commit")

        def refresh(self, _record):
            events.append("refresh")

        def rollback(self):
            events.append("rollback")

        def close(self):
            events.append("close")

    db = FakeSession()
    book = SimpleNamespace(book_id=3, title="Clean Architecture", stock=2)
    member = SimpleNamespace(user_id=5)
    loan = SimpleNamespace(
        loan_id=7,
        book_id=3,
        member_id=5,
        issue_date=None,
        due_date=None,
        returned_at=None,
        status="BORROWED",
        book=book,
        member=member,
    )

    monkeypatch.setattr(loan_service, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        loan_service.book_repository,
        "get_book_for_update",
        lambda session, _book_id: book if session is db else None,
    )
    monkeypatch.setattr(
        loan_service.user_repository,
        "get_member",
        lambda session, _member_id: member if session is db else None,
    )

    def decrease_stock(session, _book_id):
        assert session is db
        events.append("decrease-stock")

    def create_loan(session, **_fields):
        assert session is db
        events.append("create-loan")
        return loan

    monkeypatch.setattr(
        loan_service.book_repository,
        "decrease_stock",
        decrease_stock,
    )
    monkeypatch.setattr(loan_service.loan_repository, "create_loan", create_loan)

    result = loan_service.loan_book(book_id=3, member_id=5, days=14)

    assert result["loan_id"] == 7
    assert events == [
        "decrease-stock",
        "create-loan",
        "commit",
        "refresh",
        "close",
    ]
