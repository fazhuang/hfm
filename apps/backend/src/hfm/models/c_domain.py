"""C-domain model — 《针灸甲乙经》历史知识体系 (P1-05 — E-05).

Implements the frozen P1-05 acceptance criterion: historical
disease/point/meridian/technique retrieval returns source/version/citation;
no diagnosis, treatment, ranking or prescription (AB-14 / ADR-02 Guard-02).

  - CDomainTerm: a structured historical record (病证 / 穴位 / 经络 / 刺灸法 /
    章节) with typed-Entity stable identity (entity_id → entities.id,
    I5). The term is anchored to the versioned literature through an
    optional canonical_passage_id (P1-04 reuse — the source text that
    documents the term).
  - CDomainRelation: a structured historical relation between two C terms
    (e.g. 穴位位于经络 / 章节记载病证) with evidence binding
    (evidence_id → evidences.id, P1-02 reuse). Relations are immutable
    (I4) — a correction is a new relation.

All fields are canonical research metadata only; there is deliberately no
diagnosis / treatment / prescription / ranking column anywhere in the
C-domain (AB-14). Public visibility is defined solely by the P1-09
publication state of an admitted ContentArtifact bound to the term's Entity
(no parallel publication store — AB-03/AB-07).
"""

from __future__ import annotations

import enum
from typing import ClassVar

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class CDomainTermType(enum.StrEnum):
    """Canonical C-domain term families (historical classification only)."""

    disease_symptom = "disease_symptom"  # 病证
    acupoint = "acupoint"  # 穴位
    meridian = "meridian"  # 经络
    technique = "technique"  # 刺灸法
    chapter_section = "chapter_section"  # 章节


class CDomainRelationType(enum.StrEnum):
    """Structured historical relations among C terms (no clinical semantics)."""

    located_in = "located_in"  # 位于（穴位→经络）
    recorded_in = "recorded_in"  # 记载于（病证→章节）
    associated_with = "associated_with"  # 关联（泛化历史关系）
    cross_reference = "cross_reference"  # 互参


_TERM_TYPE_VALUES = ", ".join(f"'{t.value}'" for t in CDomainTermType)
_RELATION_TYPE_VALUES = ", ".join(f"'{r.value}'" for r in CDomainRelationType)


class CDomainTerm(BaseModel):
    """A structured historical C-domain record (《针灸甲乙经》术语)."""

    __tablename__ = "c_domain_terms"
    __table_args__ = (
        UniqueConstraint("entity_id", name="uq_c_domain_terms_entity_id"),
        CheckConstraint(
            f"term_type IN ({_TERM_TYPE_VALUES})",
            name="ck_c_domain_terms_term_type",
        ),
    )

    #: identity + classification + literature anchor are immutable (I4/I5).
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {"id", "entity_id", "term_type", "term_name", "canonical_passage_id"}
    )

    @validates("entity_id", "term_type", "term_name", "canonical_passage_id")
    def _validate_immutable(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # id-based guard: once persisted, any change from the loaded state is rejected
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new C-domain term")
        return value

    entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
        comment="稳定标识（= entities.id，1:1 UNIQUE；EntityType.concept/acupoint，I5）",
    )
    term_type: Mapped[CDomainTermType] = mapped_column(
        String(30),
        nullable=False,
        comment="术语家族: disease_symptom/acupoint/meridian/technique/chapter_section",
    )
    term_name: Mapped[str] = mapped_column(
        String(300), nullable=False, comment="术语名称（历史记录）"
    )
    canonical_passage_id: Mapped[str | None] = mapped_column(
        ForeignKey("passages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="P1-04 复用：记载该术语的版本化原文段落（source/version 锚点）",
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="历史语义说明（无临床建议语义）"
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="provenance 录入者引用占位（CA-026 桥；无 User FK — Auth 红线）",
    )


class CDomainRelation(BaseModel):
    """A structured historical relation between two C-domain terms."""

    __tablename__ = "c_domain_relations"
    __table_args__ = (
        CheckConstraint(
            f"relation_type IN ({_RELATION_TYPE_VALUES})",
            name="ck_c_domain_relations_relation_type",
        ),
        CheckConstraint(
            "source_term_entity_id <> target_term_entity_id",
            name="ck_c_domain_relations_not_self",
        ),
    )

    #: structural binding + evidence anchor are immutable (I4).
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {"id", "source_term_entity_id", "target_term_entity_id", "relation_type", "evidence_id"}
    )

    @validates("source_term_entity_id", "target_term_entity_id", "relation_type", "evidence_id")
    def _validate_immutable_binding(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # id-based guard: once persisted, any change from the loaded state is rejected
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new C-domain relation")
        return value

    source_term_entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="关系源（C 术语 Entity）",
    )
    target_term_entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="关系目标（C 术语 Entity）",
    )
    relation_type: Mapped[CDomainRelationType] = mapped_column(
        String(30),
        nullable=False,
        comment="历史关系类型: located_in/recorded_in/associated_with/cross_reference",
    )
    evidence_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidences.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="P1-02 证据绑定（公开投影仅暴露带证据的历史关系）",
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="关系阐述（历史语境）"
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="provenance 录入者引用占位（CA-026 桥；无 User FK — Auth 红线）",
    )
