"""CD-5: add withdrawal state to sources / versions

Revision ID: 0007
Revises: 0006

Completes the Frozen withdrawal semantics required by Citation I2 gate:
HFM-CANONICAL-DOMAIN-MODEL-v0.1.md (withdrawn Version) and
HFM-EVIDENCE-LINEAGE-CONTRACT-v0.1.md §2.5 (withdrawn Source → Evidence
taint → Citation rejected).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sources",
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "versions",
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("versions", "withdrawn_at")
    op.drop_column("sources", "withdrawn_at")
