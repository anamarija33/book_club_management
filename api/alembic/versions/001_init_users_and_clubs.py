"""init users and clubs

Revision ID: 001
Revises:
Create Date: 2026-03-02

Prva migracija — kreira tablice users i clubs.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("hours_per_week", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("pages_per_week", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "clubs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_members", sa.Integer(), nullable=False),
        sa.Column("min_hours_per_week", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("pages_per_week", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("registration_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("name", name="uq_clubs_name"),
    )


def downgrade() -> None:
    op.drop_table("clubs")
    op.drop_table("users")
