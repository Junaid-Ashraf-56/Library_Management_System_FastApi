import asyncio
import os

import pytest

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://library:library@localhost/library_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.main import domain_error_handler
from app.service import book_service, loan_service


def test_book_service_uses_domain_validation_error():
    with pytest.raises(ValidationError, match="Stock cannot be negative"):
        book_service.add_book(
            title="Book",
            author="Author",
            category="Category",
            price=10,
            publish_year=2020,
            stock=-1,
        )


def test_loan_service_uses_domain_validation_error():
    with pytest.raises(ValidationError, match="at least one day"):
        loan_service.loan_book(book_id=1, member_id=1, days=0)


@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (ValidationError("invalid"), 400),
        (AuthenticationError("invalid credentials"), 401),
        (AuthorizationError("forbidden"), 403),
        (NotFoundError("missing"), 404),
        (ConflictError("conflict"), 409),
    ],
)
def test_domain_exceptions_map_to_http_statuses(exception, expected_status):
    response = asyncio.run(domain_error_handler(None, exception))
    assert response.status_code == expected_status
