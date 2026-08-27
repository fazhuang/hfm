"""CD-1: entities / persons

Revision ID: 0002
Revises: 0001

Corresponds to the frozen CD-1 scope (HFM-PHASE0.4-CORE-MIGRATION-DAG.md):
Entity + EntityType + Person (typed entity, no catch-all schema).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("name_zh", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "entity_type IN ('person', 'work', 'place', 'institution', 'concept', 'acupoint', "
            "'event')",
            name="ck_entities_entity_type",
        ),
    )
    op.create_index("ix_entities_entity_type", "entities", ["entity_type"])
    op.create_table(
        "persons",
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("name_pinyin", sa.String(length=200), nullable=True),
        sa.Column("name_zh", sa.String(length=200), nullable=True),
        sa.Column("courtesy_name", sa.String(length=200), nullable=True),
        sa.Column("pseudonym", sa.String(length=200), nullable=True),
        sa.Column("dynasty", sa.String(length=100), nullable=True),
        sa.Column("domain_status", sa.String(length=30), nullable=False),
        sa.Column("anchor_path", sa.Text(), nullable=True),
        sa.Column("research_relation_role", sa.String(length=100), nullable=True),
        sa.Column("domain_relation_summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("entity_id"),
    )


def downgrade() -> None:
    op.drop_table("persons")
    op.drop_index("ix_entities_entity_type", table_name="entities")
    op.drop_table("entities")
