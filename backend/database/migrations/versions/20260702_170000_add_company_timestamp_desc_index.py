"""add company timestamp desc index

Revision ID: 20260702_170000
Revises: 20260702_134454
Create Date: 2026-07-02 17:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260702_170000"
down_revision: str | None = "20260702_134454"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_stock_prices_company_timestamp_desc",
        "stock_prices",
        ["company_id", sa.text("timestamp DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_stock_prices_company_timestamp_desc", table_name="stock_prices")
