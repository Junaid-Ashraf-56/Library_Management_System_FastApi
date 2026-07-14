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
from app.routes import loan_routes
from app.schemas import LoanCreate
from app.tasks import receipt_tasks


LOAN_SNAPSHOT = {
    "loan_id": 7,
    "book_id": 3,
    "member_id": 5,
    "issue_date": "2026-07-14T10:00:00Z",
    "due_date": "2026-07-28T10:00:00Z",
    "returned_at": None,
    "status": "BORROWED",
    "book": {
        "book_id": 3,
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "category": "Software",
        "price": 34.5,
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


def test_receipt_task_creates_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(receipt_tasks, "RECEIPTS_DIR", tmp_path)

    result = receipt_tasks.generate_borrow_receipt.apply(
        args=[LOAN_SNAPSHOT],
        task_id="receipt-task-id",
    ).get()

    receipt = tmp_path / "loan_7_receipt-task-id.pdf"
    assert receipt.read_bytes().startswith(b"%PDF")
    assert result["pdf_download_url"].endswith(receipt.name)


def test_borrow_enqueues_only_after_service_returns(monkeypatch):
    events = []

    def save_committed_loan(**_kwargs):
        events.append("service-returned")
        return LOAN_SNAPSHOT

    def enqueue(snapshot):
        events.append("task-enqueued")
        assert snapshot["loan_id"] == 7
        return SimpleNamespace(id="job-123")

    monkeypatch.setattr(loan_routes.loan_service, "loan_book", save_committed_loan)
    monkeypatch.setattr(loan_routes.generate_borrow_receipt, "delay", enqueue)

    response = loan_routes.loan_book(
        LoanCreate(book_id=3, days=14),
        SimpleNamespace(user_id=5, role=UserRole.MEMBER),
    )

    assert events == ["service-returned", "task-enqueued"]
    assert response["job_id"] == "job-123"


def test_successful_job_status_returns_download_url(monkeypatch):
    job = SimpleNamespace(
        status="SUCCESS",
        result={
            "message": "Receipt generated successfully.",
            "pdf_download_url": "/generated/receipts/loan_7.pdf",
        },
        successful=lambda: True,
        failed=lambda: False,
    )
    monkeypatch.setattr(loan_routes, "AsyncResult", lambda *_args, **_kwargs: job)

    response = loan_routes.get_receipt_job_status("job-123", SimpleNamespace())

    assert response["task_status"] == "SUCCESS"
    assert response["pdf_download_url"] == "/generated/receipts/loan_7.pdf"
