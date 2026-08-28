"""CD-4: assertions + assertion_evidences

Revision ID: 0005
Revises: 0004

Corresponds to the frozen CD-4 scope (HFM-PHASE0.4-CORE-MIGRATION-DAG.md):
Assertion contract (I3 coexistence, I4 no-silent-overwrite, I1 provenance).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assertions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("subject_entity_id", sa.String(length=36), nullable=False),
        sa.Column("predicate", sa.String(length=200), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("object_entity_id", sa.String(length=36), nullable=True),
        sa.Column("assertion_type", sa.String(length=30), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("editorial_status", sa.String(length=20), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "assertion_type IN ('biographical', 'textual', 'relational', 'historical', 'general')",
            name="ck_assertions_assertion_type",
        ),
        sa.CheckConstraint(
            "editorial_status IN ('draft', 'reviewed', 'approved', 'withdrawn')",
            name="ck_assertions_editorial_status",
        ),
        sa.CheckConstraint(
            "confidence IN ('low', 'medium', 'high')",
            name="ck_assertions_confidence",
        ),
        sa.CheckConstraint(
            "value IS NOT NULL OR object_entity_id IS NOT NULL",
            name="ck_assertions_value_or_object",
        ),
        sa.ForeignKeyConstraint(["object_entity_id"], ["entities.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["subject_entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assertions_subject_entity_id", "assertions", ["subject_entity_id"])
    op.create_index("ix_assertions_object_entity_id", "assertions", ["object_entity_id"])
    op.create_table(
        "assertion_evidences",
        sa.Column("assertion_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["assertion_id"], ["assertions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidences.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("assertion_id", "evidence_id"),
    )


def downgrade() -> None:
    op.drop_table("assertion_evidences")
    op.drop_index("ix_assertions_object_entity_id", table_name="assertions")
    op.drop_index("ix_assertions_subject_entity_id", table_name="assertions")
    op.drop_table("assertions")
