"""CD-5: citations

Revision ID: 0006
Revises: 0005

Corresponds to the frozen CD-5 scope (HFM-PHASE0.4-CORE-MIGRATION-DAG.md):
Citation (target=Assertion, pinned Version, I2 reproducibility).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "citations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("target_assertion_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=True),
        sa.Column("version_id", sa.String(length=36), nullable=True),
        sa.Column("passage_id", sa.String(length=36), nullable=True),
        sa.Column("quote_text", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidences.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["passage_id"], ["passages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_assertion_id"], ["assertions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["version_id"], ["versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_citations_target_assertion_id", "citations", ["target_assertion_id"])
    op.create_index("ix_citations_evidence_id", "citations", ["evidence_id"])
    op.create_index("ix_citations_version_id", "citations", ["version_id"])
    op.create_index("ix_citations_passage_id", "citations", ["passage_id"])


def downgrade() -> None:
    op.drop_index("ix_citations_passage_id", table_name="citations")
    op.drop_index("ix_citations_version_id", table_name="citations")
    op.drop_index("ix_citations_evidence_id", table_name="citations")
    op.drop_index("ix_citations_target_assertion_id", table_name="citations")
    op.drop_table("citations")
