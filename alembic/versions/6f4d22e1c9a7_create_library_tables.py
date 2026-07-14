"""create library tables

Revision ID: 6f4d22e1c9a7
Revises: 15956caf893b
Create Date: 2026-07-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import context, op

revision: str = "6f4d22e1c9a7"
down_revision: Union[str, Sequence[str], None] = "15956caf893b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = None
    if not context.is_offline_mode():
        inspector = sa.inspect(op.get_bind())

    if inspector is None or not inspector.has_table("books"):
        op.create_table(
            "books",
            sa.Column("book_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("author", sa.String(length=255), nullable=False),
            sa.Column("category", sa.String(length=100), nullable=False),
            sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("publish_year", sa.Integer(), nullable=False),
            sa.Column("stock", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("book_id"),
        )

    if inspector is None or not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("phone_number", sa.String(length=20), nullable=False),
            sa.Column("password", sa.String(length=255), nullable=False),
            sa.Column(
                "role",
                sa.Enum("MEMBER", "LIBRARIAN", name="userrole"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("user_id"),
            sa.UniqueConstraint("email"),
        )

    if inspector is None or not inspector.has_table("loans"):
        op.create_table(
            "loans",
            sa.Column("loan_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("book_id", sa.Integer(), nullable=False),
            sa.Column("member_id", sa.Integer(), nullable=False),
            sa.Column(
                "issue_date",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("due_date", sa.DateTime(), nullable=False),
            sa.Column("returned_at", sa.DateTime(), nullable=True),
            sa.Column(
                "status",
                sa.Enum("BORROWED", "RETURNED", "OVERDUE", name="loanstatus"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["book_id"], ["books.book_id"]),
            sa.ForeignKeyConstraint(["member_id"], ["users.user_id"]),
            sa.PrimaryKeyConstraint("loan_id"),
        )


def downgrade() -> None:
    op.drop_table("loans")
    op.drop_table("users")
    op.drop_table("books")
    op.execute("DROP TYPE IF EXISTS loanstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
