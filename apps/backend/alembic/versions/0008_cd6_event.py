"""CD-6: events / event_relations / event_assertions

Revision ID: 0008
Revises: 0007

Implements Frozen CD-6 (Person/Event 关系):
  - events (typed-Entity extension: entity_id PK 1:1 → entities.id,
    event_type + canonical temporal frame with per-bound precision,
    approximate flags);
  - event_relations (Person/Event 关系, ADAPT CA-001 AcademicRelation);
  - event_assertions (Event → Assertion aggregation, 事件证据链).

Temporal frame constraints (Frozen CD-6 gates 时间区间 + 精度):
precision↔nullability consistency, month/day/year ranges, start<=end
(open intervals allowed), role values, no self-relation.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None

_EVENT_TYPES = (
    "birth",
    "death",
    "study",
    "career",
    "marriage",
    "travel",
    "composition",
    "meeting",
    "other",
)
_PRECISIONS = ("unknown", "year", "month", "day")
_ROLES = ("actor", "participant", "witness", "other")


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("start_year", sa.Integer(), nullable=True),
        sa.Column("start_month", sa.Integer(), nullable=True),
        sa.Column("start_day", sa.Integer(), nullable=True),
        sa.Column(
            "start_precision",
            sa.String(20),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column(
            "start_approximate",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("end_month", sa.Integer(), nullable=True),
        sa.Column("end_day", sa.Integer(), nullable=True),
        sa.Column(
            "end_precision",
            sa.String(20),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column(
            "end_approximate",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
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
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("entity_id", name="uq_events_entity_id"),
        sa.CheckConstraint(
            f"event_type IN ({', '.join(repr(t) for t in _EVENT_TYPES)})",
            name="ck_events_event_type",
        ),
        sa.CheckConstraint(
            f"start_precision IN ({', '.join(repr(p) for p in _PRECISIONS)})",
            name="ck_events_start_precision",
        ),
        sa.CheckConstraint(
            f"end_precision IN ({', '.join(repr(p) for p in _PRECISIONS)})",
            name="ck_events_end_precision",
        ),
        sa.CheckConstraint(
            "(start_precision = 'unknown' AND start_year IS NULL"
            " AND start_month IS NULL AND start_day IS NULL)"
            " OR (start_precision = 'year' AND start_year IS NOT NULL"
            " AND start_month IS NULL AND start_day IS NULL)"
            " OR (start_precision = 'month' AND start_year IS NOT NULL"
            " AND start_month IS NOT NULL AND start_day IS NULL)"
            " OR (start_precision = 'day' AND start_year IS NOT NULL"
            " AND start_month IS NOT NULL AND start_day IS NOT NULL)",
            name="ck_events_start_consistency",
        ),
        sa.CheckConstraint(
            "(end_precision = 'unknown' AND end_year IS NULL"
            " AND end_month IS NULL AND end_day IS NULL)"
            " OR (end_precision = 'year' AND end_year IS NOT NULL"
            " AND end_month IS NULL AND end_day IS NULL)"
            " OR (end_precision = 'month' AND end_year IS NOT NULL"
            " AND end_month IS NOT NULL AND end_day IS NULL)"
            " OR (end_precision = 'day' AND end_year IS NOT NULL"
            " AND end_month IS NOT NULL AND end_day IS NOT NULL)",
            name="ck_events_end_consistency",
        ),
        sa.CheckConstraint(
            "(start_month IS NULL OR start_month BETWEEN 1 AND 12)"
            " AND (end_month IS NULL OR end_month BETWEEN 1 AND 12)",
            name="ck_events_month_range",
        ),
        sa.CheckConstraint(
            "(start_day IS NULL OR start_day BETWEEN 1 AND 31)"
            " AND (end_day IS NULL OR end_day BETWEEN 1 AND 31)",
            name="ck_events_day_range",
        ),
        sa.CheckConstraint(
            "(start_year IS NULL OR start_year BETWEEN -9999 AND 9999)"
            " AND (end_year IS NULL OR end_year BETWEEN -9999 AND 9999)",
            name="ck_events_year_range",
        ),
        sa.CheckConstraint(
            "start_year IS NULL OR end_year IS NULL"
            " OR (start_year, COALESCE(start_month, 1), COALESCE(start_day, 1))"
            " <= (end_year, COALESCE(end_month, 1), COALESCE(end_day, 1))",
            name="ck_events_start_le_end",
        ),
    )

    op.create_table(
        "event_relations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("event_id", sa.String(36), nullable=False),
        sa.Column("relation_role", sa.String(20), nullable=False),
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
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["event_id"], ["events.entity_id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("entity_id", "event_id", "relation_role", name="uq_event_relations"),
        sa.CheckConstraint(
            f"relation_role IN ({', '.join(repr(r) for r in _ROLES)})",
            name="ck_event_relations_role",
        ),
        sa.CheckConstraint("entity_id <> event_id", name="ck_event_relations_not_self"),
    )
    op.create_index("ix_event_relations_entity_id", "event_relations", ["entity_id"])
    op.create_index("ix_event_relations_event_id", "event_relations", ["event_id"])

    op.create_table(
        "event_assertions",
        sa.Column("event_id", sa.String(36), primary_key=True),
        sa.Column("assertion_id", sa.String(36), primary_key=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.entity_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assertion_id"], ["assertions.id"], ondelete="CASCADE"),
    )

    # SQLite-only backstop: event evidence aggregate = assertions ABOUT the
    # event (subject_entity_id == event_id). A CHECK cannot express the join,
    # so an insert trigger enforces it at the DB layer (§35 strong probes);
    # the repository raises ValueError first. PostgreSQL relies on the
    # repository guard (no portable trigger).
    if op.get_bind().dialect.name == "sqlite":
        op.execute(
            "CREATE TRIGGER IF NOT EXISTS trg_event_assertions_subject_match"
            " BEFORE INSERT ON event_assertions"
            " FOR EACH ROW"
            " WHEN NOT EXISTS (SELECT 1 FROM assertions"
            "   WHERE id = NEW.assertion_id AND subject_entity_id = NEW.event_id)"
            " BEGIN SELECT RAISE(ABORT, 'event_assertions subject mismatch'); END"
        )


def downgrade() -> None:
    op.drop_table("event_assertions")
    op.drop_index("ix_event_relations_event_id", table_name="event_relations")
    op.drop_index("ix_event_relations_entity_id", table_name="event_relations")
    op.drop_table("event_relations")
    op.drop_table("events")
