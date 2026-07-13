import os
from types import SimpleNamespace

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://library:library@localhost/library_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

from app.model.enums import UserRole
from app.routes import library_routes
from app.schemas import LoanCreate
from app.tasks import receipt_tasks


LOAN_SNAPSHOT = {
    "loan_id": 7,
    "book_id": 3,
    "member_id": 5,
    "issue_date": "2026-07-13T10:00:00+00:00",
    "due_date": "2026-07-27T10:00:00+00:00",
    "returned_at": None,
    "status": "BORROWED",
    "book": {
        "book_id": 3,
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "category": "Software",
        "price": 34.50,
        "publish_year": 2017,
        "stock": 1,
    },
    "member": {
        "user_id": 5,
        "name": "Ayesha Khan",
        "email": "ayesha@example.com",
        "phone_number": "555-0101",
        "role": "MEMBER",
    },
}


def test_receipt_task_creates_pdf_and_returns_download_url(tmp_path, monkeypatch):
    monkeypatch.setattr(receipt_tasks, "RECEIPTS_DIR", tmp_path)

    result = receipt_tasks.generate_borrow_receipt.apply(
        args=[LOAN_SNAPSHOT],
        task_id="receipt-task-id",
    ).get()

    receipt = tmp_path / "loan_7_receipt-task-id.pdf"
    assert receipt.read_bytes().startswith(b"%PDF")
    assert result == {
        "message": "Receipt generated successfully.",
        "pdf_download_url": "/generated/receipts/loan_7_receipt-task-id.pdf",
    }


def test_borrow_enqueues_receipt_after_service_returns(monkeypatch):
    events = []

    def save_loan(**_kwargs):
        events.append("committed-loan-returned")
        return LOAN_SNAPSHOT

    def enqueue(snapshot):
        events.append("receipt-enqueued")
        assert snapshot["loan_id"] == LOAN_SNAPSHOT["loan_id"]
        assert snapshot["book"]["title"] == LOAN_SNAPSHOT["book"]["title"]
        assert snapshot["member"]["name"] == LOAN_SNAPSHOT["member"]["name"]
        assert snapshot["issue_date"] == "2026-07-13T10:00:00Z"
        return SimpleNamespace(id="job-123")

    monkeypatch.setattr(library_routes.library_service, "loan_book", save_loan)
    monkeypatch.setattr(library_routes.generate_borrow_receipt, "delay", enqueue)

    response = library_routes.loan_book(
        LoanCreate(book_id=3, days=14),
        SimpleNamespace(user_id=5, role=UserRole.MEMBER),
    )

    assert events == ["committed-loan-returned", "receipt-enqueued"]
    assert response["job_id"] == "job-123"
    assert response["message"] == "Receipt is being generated."


def test_successful_job_status_contains_pdf_url(monkeypatch):
    job = SimpleNamespace(
        status="SUCCESS",
        result={
            "message": "Receipt generated successfully.",
            "pdf_download_url": "/generated/receipts/loan_7.pdf",
        },
        successful=lambda: True,
        failed=lambda: False,
    )
    monkeypatch.setattr(library_routes, "AsyncResult", lambda *_args, **_kwargs: job)

    response = library_routes.get_job_status("job-123", SimpleNamespace())

    assert response == {
        "job_id": "job-123",
        "task_status": "SUCCESS",
        "message": "Receipt generated successfully.",
        "pdf_download_url": "/generated/receipts/loan_7.pdf",
    }
