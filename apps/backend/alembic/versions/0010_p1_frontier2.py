"""P1 Frontier-2: identity/RBAC (P1-10), publication (P1-09), evidence binding (P1-02)

Revision ID: 0010
Revises: 0009

Adds:
  - users / roles / user_roles / role_permissions (HFM-native 5-role RBAC, ADR-07);
  - publication_records (review/approve/publish/withdraw lifecycle, P1-09);
  - evidences.artifact_id (Source→Artifact→Version→Evidence chain binding, P1-02);
  - PostgreSQL-only pg_trgm + GIN/B-Tree search indexes (ADR-02) — guarded by
    dialect so the SQLite test path is unaffected; search predicates remain
    portable (ILIKE) and testable on SQLite.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None

_ROLES = (
    "ANONYMOUS_VISITOR",
    "STUDENT_RESEARCHER",
    "SCHOLAR_RESEARCHER",
    "CONTENT_REVIEWER",
    "SYSTEM_ADMIN",
)
_STATUS = ("PENDING_REVIEW", "APPROVED", "REJECTED", "PUBLISHED", "WITHDRAWN")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
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
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.CheckConstraint("is_active IN (0, 1)", name="ck_users_is_active"),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
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
        sa.UniqueConstraint("code", name="uq_roles_code"),
        sa.CheckConstraint(f"code IN ({', '.join(repr(r) for r in _ROLES)})", name="ck_roles_code"),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("role_id", sa.String(36), primary_key=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.String(36), primary_key=True),
        sa.Column("permission_code", sa.String(60), primary_key=True),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "publication_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("artifact_id", sa.String(36), nullable=False),
        sa.Column(
            "publication_status",
            sa.String(30),
            nullable=False,
            server_default="PENDING_REVIEW",
        ),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("review_decision", sa.String(20), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["artifact_id"], ["content_artifacts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("artifact_id", name="uq_publication_records_artifact"),
        sa.CheckConstraint(
            f"publication_status IN ({', '.join(repr(s) for s in _STATUS)})",
            name="ck_publication_records_status",
        ),
    )
    op.create_index(
        "ix_publication_records_artifact_id",
        "publication_records",
        ["artifact_id"],
    )
    with op.batch_alter_table("evidences") as batch_op:
        batch_op.add_column(sa.Column("artifact_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_evidences_artifact_id",
            "content_artifacts",
            ["artifact_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_evidences_artifact_id", ["artifact_id"])

    # PostgreSQL-only search indexes (ADR-02): pg_trgm GIN on searchable text
    # columns + composite B-Tree on publication/rights/active predicates.
    # SQLite (test path) is unaffected — search predicates are portable ILIKE.
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_passages_content_trgm "
            "ON passages USING gin (content_text gin_trgm_ops)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_passages_pub_rights_active "
            "ON passages (publication_status, rights_status, is_active)"
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_passages_pub_rights_active")
        op.execute("DROP INDEX IF EXISTS ix_passages_content_trgm")
    with op.batch_alter_table("evidences") as batch_op:
        batch_op.drop_index("ix_evidences_artifact_id")
        batch_op.drop_constraint("fk_evidences_artifact_id", type_="foreignkey")
        batch_op.drop_column("artifact_id")
    op.drop_index("ix_publication_records_artifact_id", table_name="publication_records")
    op.drop_table("publication_records")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("roles")
    op.drop_table("users")
