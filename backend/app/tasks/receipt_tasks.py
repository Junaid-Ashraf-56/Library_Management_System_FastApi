from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import wrap
from uuid import uuid4

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.celery_app import celery_app
from app.core.paths import RECEIPTS_DIR


def _format_datetime(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.strftime("%d %B %Y, %H:%M %Z")


def _draw_field(pdf: canvas.Canvas, label: str, value: str, y: float) -> float:
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(72, y, label)
    pdf.setFont("Helvetica", 11)

    lines = wrap(value, width=62) or [""]
    for index, line in enumerate(lines):
        pdf.drawString(190, y - (index * 16), line)

    return y - max(28, len(lines) * 16)


@celery_app.task(
    bind=True,
    name="loans.generate_borrow_receipt",
    autoretry_for=(OSError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_borrow_receipt(self, loan: dict) -> dict[str, str]:
    """Create a PDF from a JSON-safe snapshot of a committed loan."""
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

    task_id = self.request.id or str(uuid4())
    filename = f"loan_{loan['loan_id']}_{task_id}.pdf"
    receipt_path = RECEIPTS_DIR / filename
    temporary_path = Path(f"{receipt_path}.tmp")

    pdf = canvas.Canvas(str(temporary_path), pagesize=A4)
    page_width, page_height = A4
    pdf.setTitle(f"Borrow receipt - loan {loan['loan_id']}")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(page_width / 2, page_height - 72, "Library Borrow Receipt")
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 92,
        f"Receipt for loan #{loan['loan_id']}",
    )

    fields = (
        ("Book", loan["book"]["title"]),
        ("Author", loan["book"]["author"]),
        ("Member", loan["member"]["name"]),
        ("Member email", loan["member"]["email"]),
        ("Borrow date", _format_datetime(loan["issue_date"])),
        ("Due date", _format_datetime(loan["due_date"])),
        ("Loan status", loan["status"]),
    )

    y = page_height - 140
    for label, value in fields:
        y = _draw_field(pdf, label, str(value), y)

    pdf.line(72, y, page_width - 72, y)
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(72, y - 24, "Please return the book on or before the due date.")
    pdf.save()
    temporary_path.replace(receipt_path)

    return {
        "message": "Receipt generated successfully.",
        "pdf_download_url": f"/generated/receipts/{filename}",
    }
