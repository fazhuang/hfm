"""CD-0 foundation: sources / source_refs / institutions

Revision ID: 0001
Revises:
Create Date: 2026-08-27

Corresponds to the frozen CD-0 scope (HFM-PHASE0.4-CORE-MIGRATION-DAG.md):
immutable Source identity, SourceRef (anchored to Source), Institution.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_key", sa.String(length=200), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_uri", sa.String(length=1000), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("rights_basis", sa.String(length=500), nullable=True),
        sa.Column("allowed_scope", sa.String(length=500), nullable=True),
        sa.Column("authorization_basis", sa.Text(), nullable=True),
        sa.Column("legacy_source_key", sa.String(length=200), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_key", name="uq_sources_source_key"),
    )
    op.create_table(
        "institutions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "research",
                "university",
                "archive",
                "institution",
                name="institution_type",
                native_enum=False,
                length=30,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "active",
                "archived",
                "deleted",
                name="institution_status",
                native_enum=False,
                length=30,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "type IN ('research', 'university', 'archive', 'institution')",
            name="ck_institutions_type",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived', 'deleted')",
            name="ck_institutions_status",
        ),
    )
    op.create_table(
        "source_refs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("author", sa.String(length=200), nullable=True),
        sa.Column("edition_info", sa.String(length=500), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("locator", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_refs_source_id", "source_refs", ["source_id"])


def downgrade() -> None:
    op.drop_index("ix_source_refs_source_id", table_name="source_refs")
    op.drop_table("source_refs")
    op.drop_table("institutions")
    op.drop_table("sources")
