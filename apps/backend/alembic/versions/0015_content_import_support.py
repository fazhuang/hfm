"""Content import support (B05-SG-R2; SG-01/SG-02/SG-04).

Revision ID: 0015
Revises: 0014

Authorized minimal content-schema repair (Product Owner SCHEMA_DECISION=B,
governed supersession 0014 -> 0015):

  SG-01 documents: new `documents` registry (FILE != DOCUMENT != WORK !=
      EDITION) with title/author dual-track fields and unique `stable_id`.
  SG-02 stable ID persistence: nullable-unique `stable_id` on the content
      root tables the B05 import contract targets (persons, works, editions,
      evidences).
  SG-04 person aliases: new `person_aliases` (CANONICAL_PERSON -> alias +
      alias_type + source reference), never duplicating Person rows.

No content is imported; no destructive operation; downgrade drops only the
new tables/columns.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None

STABLE_ID = sa.String(120)


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("stable_id", STABLE_ID, nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("title_normalized", sa.String(500), nullable=True),
        sa.Column("author_original", sa.String(300), nullable=True),
        sa.Column("author_normalized", sa.String(300), nullable=True),
        sa.Column("publication", sa.String(300), nullable=True),
        sa.Column("year", sa.String(40), nullable=True),
        sa.Column("doc_type", sa.String(80), nullable=True),
        sa.Column("language", sa.String(20), nullable=True, server_default="zh"),
        sa.Column("edition", sa.String(300), nullable=True),
        sa.Column("source_asset_id", sa.String(36), nullable=True),
        sa.Column("source_pages", sa.String(200), nullable=True),
        sa.Column("source_sha256", sa.String(64), nullable=True),
        sa.Column("processing_status", sa.String(40), nullable=True, server_default="auto"),
        sa.Column(
            "review_status",
            sa.String(40),
            nullable=True,
            server_default="AUTO_EXTRACTED",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("uq_documents_stable_id", "documents", ["stable_id"], unique=True)

    for table in ("persons", "works", "editions", "evidences"):
        op.add_column(table, sa.Column("stable_id", STABLE_ID, nullable=True))
        op.create_index(f"uq_{table}_stable_id", table, ["stable_id"], unique=True)

    op.create_table(
        "person_aliases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "person_id",
            sa.String(36),
            sa.ForeignKey("persons.entity_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias", sa.String(200), nullable=False),
        sa.Column("alias_type", sa.String(30), nullable=False, server_default="alias"),
        sa.Column("source_asset_id", sa.String(36), nullable=True),
        sa.Column("source_location", sa.String(200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "person_id",
            "alias",
            "alias_type",
            name="uq_person_aliases_person_alias_type",
        ),
    )


def downgrade() -> None:
    op.drop_table("person_aliases")
    for table in ("evidences", "editions", "works", "persons"):
        op.drop_index(f"uq_{table}_stable_id", table_name=table)
        op.drop_column(table, "stable_id")
    op.drop_index("uq_documents_stable_id", table_name="documents")
    op.drop_table("documents")
