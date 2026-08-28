"""CD-3: evidences

Revision ID: 0004
Revises: 0003

Corresponds to the frozen CD-3 scope (HFM-PHASE0.4-CORE-MIGRATION-DAG.md):
Evidence + taint + content_hash (I1 provenance, integrity).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_level", sa.String(length=20), nullable=False),
        sa.Column("source_ref_id", sa.String(length=36), nullable=True),
        sa.Column("source_passage_id", sa.String(length=36), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("taint_status", sa.String(length=32), nullable=False, server_default="clean"),
        sa.Column("tainted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("taint_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "evidence_level IN ('LEVEL_1', 'LEVEL_2', 'LEVEL_3', 'LEVEL_4')",
            name="ck_evidences_evidence_level",
        ),
        sa.CheckConstraint(
            "taint_status IN ('clean', 'source_withdrawn', 'quarantined')",
            name="ck_evidences_taint_status",
        ),
        sa.CheckConstraint(
            "source_ref_id IS NOT NULL OR source_passage_id IS NOT NULL",
            name="ck_evidences_provenance_anchor",
        ),
        sa.ForeignKeyConstraint(["source_passage_id"], ["passages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_ref_id"], ["source_refs.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evidences_source_ref_id", "evidences", ["source_ref_id"])
    op.create_index("ix_evidences_source_passage_id", "evidences", ["source_passage_id"])


def downgrade() -> None:
    op.drop_index("ix_evidences_source_passage_id", table_name="evidences")
    op.drop_index("ix_evidences_source_ref_id", table_name="evidences")
    op.drop_table("evidences")
