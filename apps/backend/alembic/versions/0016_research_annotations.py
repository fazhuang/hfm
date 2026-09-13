"""Research annotations (P4 — research reader highlight annotation).

Revision ID: 0016
Revises: 0015

Adds ``research_annotations`` — owner-scoped personal research state bound to
a canonical passage (P1-07 reader anchor), for the P4 research workbench
highlight + note loop. Reuses the existing RBAC research namespace (no new
permission codes); no content is imported; downgrade drops only this table.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_annotations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "owner_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "passage_id",
            sa.String(36),
            sa.ForeignKey("passages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("research_projects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("quote_text", sa.Text(), nullable=True),
        sa.Column("start_offset", sa.Integer(), nullable=True),
        sa.Column("end_offset", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
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
        sa.CheckConstraint(
            "start_offset IS NULL OR end_offset IS NULL OR start_offset <= end_offset",
            name="ck_research_annotations_offsets",
        ),
    )
    op.create_index("ix_research_annotations_owner_id", "research_annotations", ["owner_id"])
    op.create_index("ix_research_annotations_passage_id", "research_annotations", ["passage_id"])
    op.create_index("ix_research_annotations_project_id", "research_annotations", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_research_annotations_project_id", table_name="research_annotations")
    op.drop_index("ix_research_annotations_passage_id", table_name="research_annotations")
    op.drop_index("ix_research_annotations_owner_id", table_name="research_annotations")
    op.drop_table("research_annotations")
