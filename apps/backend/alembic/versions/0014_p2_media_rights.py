"""P2 Frontier-2: media & rights lifecycle (P2-05)

Revision ID: 0014
Revises: 0013

Adds:
  - media_assets: media object registry with rights metadata (holder,
    license basis, restriction, expiry, publication permission), byte-hash
    binding (sha256), original/derivative self linkage
    (original_object_key -> object_key, RESTRICT), publication state
    (draft/published/withdrawn), and a deterministic redaction/watermark
    token (ADR-P2-01).

Per ADR-P2-01 binary bytes are NOT stored in the relational database — the
registry stores object keys into S3-compatible object storage; PostgreSQL
holds metadata only. Publication is fail-closed at the service layer: it
requires explicit rights metadata plus publication permission. New table
only; no destructive mutation of accepted tables; downgrade drops it.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "media_assets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("object_key", sa.String(500), nullable=False),
        sa.Column("original_object_key", sa.String(500), nullable=True),
        sa.Column("mime_type", sa.String(200), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("rights_holder", sa.String(300), nullable=False),
        sa.Column("license_basis", sa.String(300), nullable=False),
        sa.Column("restriction", sa.String(500), nullable=True),
        sa.Column("rights_expiry", sa.Date(), nullable=True),
        sa.Column(
            "publication_permission",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "publication_state",
            sa.String(20),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("redaction_token", sa.String(200), nullable=True),
        sa.Column("provenance", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["original_object_key"], ["media_assets.object_key"], ondelete="RESTRICT"
        ),
        sa.CheckConstraint(
            "publication_state IN ('draft', 'published', 'withdrawn')",
            name="ck_media_assets_state",
        ),
        sa.CheckConstraint("byte_size >= 0", name="ck_media_assets_byte_size"),
        sa.CheckConstraint("length(object_key) > 0", name="ck_media_assets_object_key"),
    )
    op.create_index("ix_media_assets_object_key", "media_assets", ["object_key"], unique=True)
    op.create_index("ix_media_assets_sha256", "media_assets", ["sha256"])
    op.create_index("ix_media_assets_state", "media_assets", ["publication_state"])


def downgrade() -> None:
    op.drop_index("ix_media_assets_state", table_name="media_assets")
    op.drop_index("ix_media_assets_sha256", table_name="media_assets")
    op.drop_index("ix_media_assets_object_key", table_name="media_assets")
    op.drop_table("media_assets")
