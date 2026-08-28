"""Assertion model (CD-4 — NEW, CA-023 + Assertion Contract).

HFM-native per HFM-ASSERTION-CONTRACT-v0.1.md: a claim about a subject that
is independently citable, traceable, and can coexist with conflicting
assertions (I3). Content-bearing fields are immutable (I4: revisions are new
assertions, never silent overwrites). Subject/object anchor to CD-1 Entities
(referential integrity — no unrestricted subject_type polymorphism).
"""

from __future__ import annotations

import enum
from typing import ClassVar

from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from hfm.db.base import Base, BaseModel
from hfm.models.evidence import Evidence


class AssertionType(enum.StrEnum):
    """Assertion families (research framing; no publication semantics)."""

    BIOGRAPHICAL = "biographical"
    TEXTUAL = "textual"
    RELATIONAL = "relational"
    HISTORICAL = "historical"
    GENERAL = "general"


class EditorialStatus(enum.StrEnum):
    """Research editorial state (NOT publication state, per Frozen Contract)."""

    draft = "draft"
    reviewed = "reviewed"
    approved = "approved"
    withdrawn = "withdrawn"


class Confidence(enum.StrEnum):
    """Research confidence (NOT a publication/review decision)."""

    low = "low"
    medium = "medium"
    high = "high"


assertion_evidences = Table(
    "assertion_evidences",
    Base.metadata,
    Column(
        "assertion_id",
        String(36),
        ForeignKey("assertions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "evidence_id", String(36), ForeignKey("evidences.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Assertion(BaseModel):
    """A claim about an Entity subject, traceable to Evidence (I1/I3/I4)."""

    __tablename__ = "assertions"
    __table_args__ = (
        CheckConstraint(
            "value IS NOT NULL OR object_entity_id IS NOT NULL",
            name="ck_assertions_value_or_object",
        ),
        CheckConstraint(
            "assertion_type IN ('biographical', 'textual', 'relational', 'historical', 'general')",
            name="ck_assertions_assertion_type",
        ),
        CheckConstraint(
            "editorial_status IN ('draft', 'reviewed', 'approved', 'withdrawn')",
            name="ck_assertions_editorial_status",
        ),
        CheckConstraint(
            "confidence IN ('low', 'medium', 'high')",
            name="ck_assertions_confidence",
        ),
    )

    #: content-bearing fields are immutable (I4) — a revision is a new assertion.
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {"id", "subject_entity_id", "predicate", "value", "object_entity_id", "assertion_type"}
    )

    @validates("predicate")
    def _validate_predicate(self, key: str, value: object) -> object:
        current = getattr(self, "predicate", None)
        if current is not None and value != current:
            raise ValueError("predicate is immutable (I4): create a new assertion")
        return value

    @validates("subject_entity_id")
    def _validate_subject(self, key: str, value: object) -> object:
        current = getattr(self, "subject_entity_id", None)
        if current is not None and value != current:
            raise ValueError("subject_entity_id is immutable (I4): create a new assertion")
        return value

    subject_entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="主张主体（CD-1 Entity，参照完整性）",
    )
    predicate: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="谓词（如 born_in/authored/studied_under）"
    )
    value: Mapped[str | None] = mapped_column(Text, nullable=True, comment="字面值主张")
    object_entity_id: Mapped[str | None] = mapped_column(
        ForeignKey("entities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="关系型主张目标（CD-1 Entity）",
    )
    assertion_type: Mapped[AssertionType] = mapped_column(
        Enum(
            AssertionType,
            native_enum=False,
            length=30,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=AssertionType.GENERAL,
        comment="主张类型",
    )
    confidence: Mapped[Confidence] = mapped_column(
        Enum(
            Confidence,
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=Confidence.medium,
        comment="研究置信（非发布状态）",
    )
    editorial_status: Mapped[EditorialStatus] = mapped_column(
        Enum(
            EditorialStatus,
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=EditorialStatus.draft,
        comment="研究编辑态（非发布态）：draft/reviewed/approved/withdrawn",
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="provenance 录入者引用占位（CA-026 桥；无 User FK — Auth 红线）",
    )
    revision: Mapped[int] = mapped_column(
        default=1,
        server_default="1",
        nullable=False,
        comment="主张修订号（修订 = 新建主张，I4）",
    )

    evidences: Mapped[list[Evidence]] = relationship(
        secondary=assertion_evidences,
        lazy="selectin",
    )
