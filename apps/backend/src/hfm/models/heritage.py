"""D-domain model — 非遗传承体系 (P1-06 — E-06).

Implements the frozen P1-06 acceptance criterion: lineage relations carry
official-name, evidence and publication state; no unverified heritage /
inheritor claim is public (AB-05 cross-domain relations are explicit and
evidence/version/publication-aware).

  - HeritageProject: a 非遗项目/事项 record with typed-Entity stable
    identity (entity_id → entities.id, I5) and the official name
    (官方名称). Publication is defined solely by the P1-09 state of an
    admitted ContentArtifact bound to the project's Entity.
  - HeritageRelation: a lineage relation (传承人 / 传承主体 / 机构 affiliation)
    between a project and a person/institution Entity, carrying the
    official name, an optional time frame, and an evidence binding
    (evidence_id → evidences.id, P1-02 reuse). Relations are immutable
    (I4) — a correction is a new relation.

Public projections expose only evidenced relations on published projects;
no unverified heritage/inheritor claim is public (E-06).
"""

from __future__ import annotations

import enum
from typing import ClassVar

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class HeritageRelationRole(enum.StrEnum):
    """Typed lineage roles in a heritage relation (official-name evidence)."""

    inheritor = "inheritor"  # 传承人
    subject = "subject"  # 传承主体
    institution = "institution"  # 机构
    master = "master"  # 师父
    disciple = "disciple"  # 徒弟
    other = "other"


_ROLE_VALUES = ", ".join(f"'{r.value}'" for r in HeritageRelationRole)


class HeritageProject(BaseModel):
    """A 非遗项目/事项 (heritage project/item) with official-name identity."""

    __tablename__ = "heritage_projects"
    __table_args__ = (UniqueConstraint("entity_id", name="uq_heritage_projects_entity_id"),)

    #: identity + official naming are immutable (I4/I5).
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {"id", "entity_id", "project_name", "official_name"}
    )

    @validates("entity_id", "project_name", "official_name")
    def _validate_immutable(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new heritage project")
        return value

    entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
        comment="稳定标识（= entities.id，1:1 UNIQUE；I5）",
    )
    project_name: Mapped[str] = mapped_column(String(300), nullable=False, comment="非遗项目名称")
    official_name: Mapped[str | None] = mapped_column(
        String(300), nullable=True, comment="官方名称（official-name 证据锚点）"
    )
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="项目类别（如 传统医药/针灸）"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="项目描述（历史/传承语境）"
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="provenance 录入者引用占位（CA-026 桥；无 User FK — Auth 红线）",
    )


class HeritageRelation(BaseModel):
    """A lineage relation binding a project to a person/institution."""

    __tablename__ = "heritage_relations"
    __table_args__ = (
        CheckConstraint(
            f"relation_role IN ({_ROLE_VALUES})",
            name="ck_heritage_relations_relation_role",
        ),
        CheckConstraint(
            "project_entity_id <> subject_entity_id",
            name="ck_heritage_relations_not_self",
        ),
        CheckConstraint(
            "(start_year IS NULL AND end_year IS NULL)"
            " OR (start_year IS NOT NULL AND (end_year IS NULL OR end_year >= start_year))",
            name="ck_heritage_relations_year_order",
        ),
    )

    #: structural binding + official name + evidence anchor are immutable (I4).
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "id",
            "project_entity_id",
            "subject_entity_id",
            "relation_role",
            "official_name",
            "evidence_id",
        }
    )

    @validates(
        "project_entity_id",
        "subject_entity_id",
        "relation_role",
        "official_name",
        "evidence_id",
    )
    def _validate_immutable_binding(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new heritage relation")
        return value

    project_entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="非遗项目（HeritageProject 的 Entity 身份）",
    )
    subject_entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="传承主体（P1-03 Person Entity 或 institution Entity）",
    )
    relation_role: Mapped[HeritageRelationRole] = mapped_column(
        String(20),
        nullable=False,
        comment="传承关系角色: inheritor/subject/institution/master/disciple/other",
    )
    official_name: Mapped[str | None] = mapped_column(
        String(300), nullable=True, comment="官方名称（该传承关系的 official-name 证据）"
    )
    start_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="传承起始年（历史语境）"
    )
    end_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="传承结束年（历史语境）"
    )
    evidence_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidences.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="P1-02 证据绑定（公开投影仅暴露带证据的传承关系）",
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="关系阐述（传承语境）"
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="provenance 录入者引用占位（CA-026 桥；无 User FK — Auth 红线）",
    )
