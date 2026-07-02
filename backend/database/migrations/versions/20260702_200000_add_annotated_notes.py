"""add annotated notes

Revision ID: 20260702_200000
Revises: 20260702_170000
Create Date: 2026-07-02 20:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260702_200000"
down_revision: str | None = "20260702_180000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "annotated_notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "company_id", "date", name="uq_notes_user_company_date"),
    )
    op.create_index("ix_annotated_notes_user_id", "annotated_notes", ["user_id"])
    op.create_index("ix_annotated_notes_company_id", "annotated_notes", ["company_id"])
    op.create_index("ix_annotated_notes_date", "annotated_notes", ["date"])


def downgrade() -> None:
    op.drop_index("ix_annotated_notes_date", table_name="annotated_notes")
    op.drop_index("ix_annotated_notes_company_id", table_name="annotated_notes")
    op.drop_index("ix_annotated_notes_user_id", table_name="annotated_notes")
    op.drop_table("annotated_notes")
