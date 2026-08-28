"""CD-2: works / editions / versions / chapters / passages

Revision ID: 0003
Revises: 0002

Corresponds to the frozen CD-2 scope (HFM-PHASE0.4-CORE-MIGRATION-DAG.md):
Work / Edition / Version / Chapter / Passage + Locator (ancient text layer).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "works",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("author_entity_id", sa.String(length=36), nullable=True),
        sa.Column("dynasty", sa.String(length=100), nullable=True),
        sa.Column("composition_year_start", sa.Integer(), nullable=True),
        sa.Column("composition_year_end", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("is_extant", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["author_entity_id"], ["entities.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_works_author_entity_id", "works", ["author_entity_id"])
    op.create_table(
        "editions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("work_id", sa.String(length=36), nullable=False),
        sa.Column("edition_name", sa.String(length=500), nullable=False),
        sa.Column("era", sa.String(length=100), nullable=True),
        sa.Column("publisher_block", sa.String(length=500), nullable=True),
        sa.Column("preface_postscript", sa.Text(), nullable=True),
        sa.Column("lineage_parent_edition_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["lineage_parent_edition_id"], ["editions.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_editions_work_id", "editions", ["work_id"])
    op.create_table(
        "versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("edition_id", sa.String(length=36), nullable=False),
        sa.Column("version_name", sa.String(length=300), nullable=False),
        sa.Column("era", sa.String(length=100), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("repository", sa.String(length=500), nullable=True),
        sa.Column("shelf_mark", sa.String(length=200), nullable=True),
        sa.Column("editor", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(length=2000), nullable=True),
        sa.Column("is_formal_source", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("parent_version_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["edition_id"], ["editions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_version_id"], ["versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_versions_edition_id", "versions", ["edition_id"])
    op.create_table(
        "chapters",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("work_id", sa.String(length=36), nullable=False),
        sa.Column("parent_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapters_work_id", "chapters", ["work_id"])
    op.create_table(
        "passages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("chapter_id", sa.String(length=36), nullable=False),
        sa.Column("version_id", sa.String(length=36), nullable=True),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("translation", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tags", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"], ["versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_passages_chapter_id", "passages", ["chapter_id"])
    op.create_index("ix_passages_version_id", "passages", ["version_id"])


def downgrade() -> None:
    op.drop_index("ix_passages_version_id", table_name="passages")
    op.drop_index("ix_passages_chapter_id", table_name="passages")
    op.drop_table("passages")
    op.drop_index("ix_chapters_work_id", table_name="chapters")
    op.drop_table("chapters")
    op.drop_index("ix_versions_edition_id", table_name="versions")
    op.drop_table("versions")
    op.drop_index("ix_editions_work_id", table_name="editions")
    op.drop_table("editions")
    op.drop_index("ix_works_author_entity_id", table_name="works")
    op.drop_table("works")
