"""P1 Frontier-3: A/B domain publication binding (P1-03/P1-04) + audit/reconciliation (P1-13)

Revision ID: 0011
Revises: 0010

Adds:
  - content_artifacts.subject_entity_id (nullable FK → entities.id): binds an
    admitted artifact to a domain entity (person entity / work entity), so the
    P1-09 publication state of the artifact is the single canonical
    publication truth for the A/B domain record (no parallel publication
    store — AB-03/AB-07);
  - works.entity_id (nullable UNIQUE FK → entities.id): the typed-Entity
    stable identity (I5) for Works, matching the persons/events backbone;
  - audit_log: append-only governed-state-change journal (P1-13 auditability);
  - reconciliation_runs: recorded batch metrics + PASS/FAIL reconciliation
    results (P1-13; E-13);
  - persons.id: schema-drift alignment — migration 0002 created ``persons``
    without the surrogate ``id`` column that the accepted CD-1 ORM Person
    model declares (BaseModel UUIDv7 PK). P1-03 operates canonical person
    rows through the ORM, so the migrated shape must match the model;
    ``entity_id`` remains the semantic primary key and the new ``id``
    column is nullable for pre-existing rows.

All additions are nullable/optional columns or new append-only tables — no
canonical history is rewritten; downgrade reverses each step.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- P1-03/P1-04: domain entity binding on admitted artifacts ----------
    with op.batch_alter_table("content_artifacts") as batch_op:
        batch_op.add_column(sa.Column("subject_entity_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_content_artifacts_subject_entity_id",
            "entities",
            ["subject_entity_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_content_artifacts_subject_entity_id", ["subject_entity_id"])

    # --- P1-04: typed-Entity stable identity for Works (I5) ----------------
    with op.batch_alter_table("works") as batch_op:
        batch_op.add_column(sa.Column("entity_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_works_entity_id",
            "entities",
            ["entity_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_unique_constraint("uq_works_entity_id", ["entity_id"])
        batch_op.create_index("ix_works_entity_id", ["entity_id"])

    # --- CD-1 schema-drift alignment: persons.id (P1-03 ORM operation) -----
    # Migration 0002 created ``persons`` without the surrogate ``id`` the
    # accepted Person ORM model declares; add it so canonical person records
    # are operable through the ORM on migrated databases.
    with op.batch_alter_table("persons") as batch_op:
        batch_op.add_column(sa.Column("id", sa.String(36), nullable=True))
        batch_op.create_index("ix_persons_id", ["id"])

    # --- P1-13: append-only audit journal -----------------------------------
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(36), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("length(action) > 0", name="ck_audit_log_action_present"),
        sa.CheckConstraint("length(target_type) > 0", name="ck_audit_log_target_type_present"),
        sa.CheckConstraint("length(target_id) > 0", name="ck_audit_log_target_id_present"),
    )
    op.create_index("ix_audit_log_target_id", "audit_log", ["target_id"])
    op.create_index("ix_audit_log_actor_id", "audit_log", ["actor_id"])

    # --- P1-13: reconciliation run metrics (append-only, PASS/FAIL) ---------
    op.create_table(
        "reconciliation_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope", sa.String(100), nullable=False),
        sa.Column("expected_count", sa.Integer(), nullable=False),
        sa.Column("expected_hash", sa.String(64), nullable=False),
        sa.Column("actual_count", sa.Integer(), nullable=False),
        sa.Column("actual_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.CheckConstraint("status IN ('PASS', 'FAIL')", name="ck_reconciliation_runs_status"),
        sa.CheckConstraint(
            "expected_count >= 0 AND actual_count >= 0", name="ck_reconciliation_runs_counts"
        ),
        sa.CheckConstraint("length(scope) > 0", name="ck_reconciliation_runs_scope_present"),
        sa.CheckConstraint(
            "length(expected_hash) = 64 AND length(actual_hash) = 64",
            name="ck_reconciliation_runs_hashes",
        ),
    )
    op.create_index("ix_reconciliation_runs_scope", "reconciliation_runs", ["scope"])


def downgrade() -> None:
    op.drop_index("ix_reconciliation_runs_scope", table_name="reconciliation_runs")
    op.drop_table("reconciliation_runs")
    op.drop_index("ix_audit_log_actor_id", table_name="audit_log")
    op.drop_index("ix_audit_log_target_id", table_name="audit_log")
    op.drop_table("audit_log")

    with op.batch_alter_table("works") as batch_op:
        batch_op.drop_index("ix_works_entity_id")
        batch_op.drop_constraint("uq_works_entity_id", type_="unique")
        batch_op.drop_constraint("fk_works_entity_id", type_="foreignkey")
        batch_op.drop_column("entity_id")

    with op.batch_alter_table("persons") as batch_op:
        batch_op.drop_index("ix_persons_id")
        batch_op.drop_column("id")

    with op.batch_alter_table("content_artifacts") as batch_op:
        batch_op.drop_index("ix_content_artifacts_subject_entity_id")
        batch_op.drop_constraint("fk_content_artifacts_subject_entity_id", type_="foreignkey")
        batch_op.drop_column("subject_entity_id")
