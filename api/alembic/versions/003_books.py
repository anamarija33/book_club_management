"""add books and user_books tables

Revision ID: 003
Revises: 002
Create Date: 2026-03-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("author", sa.String(150), nullable=False),
        sa.Column("pages", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.CheckConstraint("pages > 0", name="ck_books_pages"),
    )

    op.add_column(
        "clubs",
        sa.Column(
            "current_book_id",
            sa.Integer(),
            sa.ForeignKey("books.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    op.create_table(
        "user_books",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_books")
    op.drop_column("clubs", "current_book_id")
    op.drop_table("books")
