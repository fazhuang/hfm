"""P1-01: content_artifacts — canonical content admission core

Revision ID: 0009
Revises: 0008

Implements the Phase 1 content-admission layer (AB-06 / P1-01):
  - ContentArtifact bound to a Source (required provenance) with an
    immutable content_hash (integrity; no metadata-only admission);
  - admission_state ∈ {submitted, admitted, rejected} — deliberately
    distinct from APPROVED / PUBLISHED (publication is P1-09);
  - provenance_status / rights_status / validation_result per AB invariant 1;
  - UNIQUE(source_id, content_hash) idempotency (one logical artifact);
  - rejected rows must carry a rejection_reason (fail-closed rejection log).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

_ADMISSION = ("submitted", "admitted", "rejected")
_PROVENANCE = ("pending", "verified", "failed")
_RIGHTS = (
    "public_domain",
    "customer_owned",
    "licensed",
    "third_party_permission_required",
    "unknown",
)
_VALIDATION = ("pending", "pass", "fail")


def upgrade() -> None:
    op.create_table(
        "content_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_id", sa.String(36), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("format", sa.String(50), nullable=True),
        sa.Column(
            "provenance_status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "rights_status",
            sa.String(40),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column(
            "validation_result",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "admission_state",
            sa.String(20),
            nullable=False,
            server_default="submitted",
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("version_id", sa.String(36), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["version_id"], ["versions.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("source_id", "content_hash", name="uq_content_artifacts_source_hash"),
        sa.CheckConstraint(
            f"admission_state IN ({', '.join(repr(v) for v in _ADMISSION)})",
            name="ck_content_artifacts_admission_state",
        ),
        sa.CheckConstraint(
            f"provenance_status IN ({', '.join(repr(v) for v in _PROVENANCE)})",
            name="ck_content_artifacts_provenance_status",
        ),
        sa.CheckConstraint(
            f"rights_status IN ({', '.join(repr(v) for v in _RIGHTS)})",
            name="ck_content_artifacts_rights_status",
        ),
        sa.CheckConstraint(
            f"validation_result IN ({', '.join(repr(v) for v in _VALIDATION)})",
            name="ck_content_artifacts_validation_result",
        ),
        sa.CheckConstraint(
            "content_hash IS NOT NULL AND length(content_hash) > 0"
            " OR admission_state != 'admitted'",
            name="ck_content_artifacts_content_hash_present",
        ),
        sa.CheckConstraint(
            "source_id IS NOT NULL OR admission_state != 'admitted'",
            name="ck_content_artifacts_source_present",
        ),
        sa.CheckConstraint(
            "admission_state != 'rejected' OR rejection_reason IS NOT NULL",
            name="ck_content_artifacts_rejection_has_reason",
        ),
    )
    op.create_index("ix_content_artifacts_source_id", "content_artifacts", ["source_id"])
    op.create_index("ix_content_artifacts_version_id", "content_artifacts", ["version_id"])


def downgrade() -> None:
    op.drop_index("ix_content_artifacts_version_id", table_name="content_artifacts")
    op.drop_index("ix_content_artifacts_source_id", table_name="content_artifacts")
    op.drop_table("content_artifacts")
