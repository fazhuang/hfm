"""P1 Frontier-4: C-domain terms/relations (P1-05) + heritage projects/relations (P1-06)

Revision ID: 0012
Revises: 0011

Adds:
  - c_domain_terms: structured historical C-domain records (病证/穴位/经络/
    刺灸法/章节) with typed-Entity identity (entity_id → entities.id, I5) and
    an optional canonical passage anchor (P1-04 versioned literature reuse);
  - c_domain_relations: structured historical relations among C terms with
    evidence binding (evidence_id → evidences.id, P1-02 reuse); no
    diagnosis/treatment/prescription semantics (AB-14);
  - heritage_projects: 非遗项目/事项 records with typed-Entity identity and
    official-name evidence anchor (P1-06; E-06);
  - heritage_relations: lineage relations (传承人/传承主体/机构) binding a
    project to a person/institution Entity, carrying official-name, time
    frame, and evidence binding (P1-02 reuse); public only when evidenced.

All additions are new tables (no canonical history rewritten) with
immutable binding semantics enforced at the ORM layer; downgrade reverses
each step in dependency order.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- P1-05: C-domain terms (《针灸甲乙经》历史术语) -----------------------
    op.create_table(
        "c_domain_terms",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("term_type", sa.String(30), nullable=False),
        sa.Column("term_name", sa.String(300), nullable=False),
        sa.Column("canonical_passage_id", sa.String(36), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["canonical_passage_id"], ["passages.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("entity_id", name="uq_c_domain_terms_entity_id"),
        sa.CheckConstraint(
            "term_type IN ('disease_symptom', 'acupoint', 'meridian', 'technique',"
            " 'chapter_section')",
            name="ck_c_domain_terms_term_type",
        ),
    )
    op.create_index("ix_c_domain_terms_entity_id", "c_domain_terms", ["entity_id"])
    op.create_index(
        "ix_c_domain_terms_canonical_passage_id", "c_domain_terms", ["canonical_passage_id"]
    )

    # --- P1-05: C-domain historical relations (evidence-bound) -------------
    op.create_table(
        "c_domain_relations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_term_entity_id", sa.String(36), nullable=False),
        sa.Column("target_term_entity_id", sa.String(36), nullable=False),
        sa.Column("relation_type", sa.String(30), nullable=False),
        sa.Column("evidence_id", sa.String(36), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["source_term_entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_term_entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidences.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "relation_type IN ('located_in', 'recorded_in', 'associated_with', 'cross_reference')",
            name="ck_c_domain_relations_relation_type",
        ),
        sa.CheckConstraint(
            "source_term_entity_id <> target_term_entity_id",
            name="ck_c_domain_relations_not_self",
        ),
    )
    op.create_index(
        "ix_c_domain_relations_source_term", "c_domain_relations", ["source_term_entity_id"]
    )
    op.create_index(
        "ix_c_domain_relations_target_term", "c_domain_relations", ["target_term_entity_id"]
    )
    op.create_index("ix_c_domain_relations_evidence_id", "c_domain_relations", ["evidence_id"])

    # --- P1-06: heritage projects (非遗项目/事项) ----------------------------
    op.create_table(
        "heritage_projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("project_name", sa.String(300), nullable=False),
        sa.Column("official_name", sa.String(300), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("entity_id", name="uq_heritage_projects_entity_id"),
    )
    op.create_index("ix_heritage_projects_entity_id", "heritage_projects", ["entity_id"])

    # --- P1-06: heritage lineage relations (official-name + evidence) ------
    op.create_table(
        "heritage_relations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_entity_id", sa.String(36), nullable=False),
        sa.Column("subject_entity_id", sa.String(36), nullable=False),
        sa.Column("relation_role", sa.String(20), nullable=False),
        sa.Column("official_name", sa.String(300), nullable=True),
        sa.Column("start_year", sa.Integer(), nullable=True),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("evidence_id", sa.String(36), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["project_entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_entity_id"], ["entities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidences.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "relation_role IN ('inheritor', 'subject', 'institution', 'master',"
            " 'disciple', 'other')",
            name="ck_heritage_relations_relation_role",
        ),
        sa.CheckConstraint(
            "project_entity_id <> subject_entity_id",
            name="ck_heritage_relations_not_self",
        ),
        sa.CheckConstraint(
            "(start_year IS NULL AND end_year IS NULL)"
            " OR (start_year IS NOT NULL AND (end_year IS NULL OR end_year >= start_year))",
            name="ck_heritage_relations_year_order",
        ),
    )
    op.create_index("ix_heritage_relations_project", "heritage_relations", ["project_entity_id"])
    op.create_index("ix_heritage_relations_subject", "heritage_relations", ["subject_entity_id"])
    op.create_index("ix_heritage_relations_evidence_id", "heritage_relations", ["evidence_id"])


def downgrade() -> None:
    op.drop_index("ix_heritage_relations_evidence_id", table_name="heritage_relations")
    op.drop_index("ix_heritage_relations_subject", table_name="heritage_relations")
    op.drop_index("ix_heritage_relations_project", table_name="heritage_relations")
    op.drop_table("heritage_relations")
    op.drop_index("ix_heritage_projects_entity_id", table_name="heritage_projects")
    op.drop_table("heritage_projects")

    op.drop_index("ix_c_domain_relations_evidence_id", table_name="c_domain_relations")
    op.drop_index("ix_c_domain_relations_target_term", table_name="c_domain_relations")
    op.drop_index("ix_c_domain_relations_source_term", table_name="c_domain_relations")
    op.drop_table("c_domain_relations")
    op.drop_index("ix_c_domain_terms_canonical_passage_id", table_name="c_domain_terms")
    op.drop_index("ix_c_domain_terms_entity_id", table_name="c_domain_terms")
    op.drop_table("c_domain_terms")
