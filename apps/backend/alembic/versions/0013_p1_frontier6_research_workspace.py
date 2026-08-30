"""P1 Frontier-6: research workspace (P1-12)

Revision ID: 0013
Revises: 0012

Adds:
  - research_projects: owner-scoped researcher projects (owner_id →
    users.id, RESTRICT; ADR-07 SCHOLAR_RESEARCHER scope);
  - research_notes: owner-scoped personal notes (owner_id → users.id,
    RESTRICT; optional project binding with CASCADE — deleting a project
    deletes its notes; ADR-07 STUDENT_RESEARCHER scope).

Ownership always derives from the authenticated Principal; no
client-supplied owner_id is stored. Canonical truth stores are reused —
no alternate authorization store (ADR-05/07). New tables only; no
destructive mutation of accepted tables; downgrade reverses in dependency
order (notes before projects).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- P1-12: research projects (owner-scoped) ---------------------------
    op.create_table(
        "research_projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("length(title) > 0", name="ck_research_projects_title"),
    )
    op.create_index("ix_research_projects_owner_id", "research_projects", ["owner_id"])

    # --- P1-12: research notes (owner-scoped, optional project binding) ----
    op.create_table(
        "research_notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=True),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
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
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"),
        sa.CheckConstraint("length(content) > 0", name="ck_research_notes_content"),
    )
    op.create_index("ix_research_notes_owner_id", "research_notes", ["owner_id"])
    op.create_index("ix_research_notes_project_id", "research_notes", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_research_notes_project_id", table_name="research_notes")
    op.drop_index("ix_research_notes_owner_id", table_name="research_notes")
    op.drop_table("research_notes")
    op.drop_index("ix_research_projects_owner_id", table_name="research_projects")
    op.drop_table("research_projects")
