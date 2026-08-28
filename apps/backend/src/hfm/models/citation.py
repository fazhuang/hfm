"""Citation model (CD-5 — ADAPT, CA-022 + Evidence Lineage §2.3).

ADAPT of HFB `models/academic_evidence.py::Citation` @ `03755b5`:
  - retained: quote_text / note fields;
  - removed: polymorphic target (target_type/target_id over
    Variant/AcademicRelation/Passage) — unified to target=Assertion (CD-4);
  - rewritten: HFM Citation is a reproducible reference — pinned Version /
    Passage (CD-2) + optional direct Evidence edge (CD-3); binding fields
    are immutable (I4); new citations to withdrawn Assertions are rejected
    (withdrawn-reference gate).
"""

from __future__ import annotations

from typing import ClassVar

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class Citation(BaseModel):
    """A reproducible reference to an Assertion (with pinned text location)."""

    __tablename__ = "citations"

    #: reference-binding fields are immutable (I4) — a correction is a new citation.
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "id",
            "target_assertion_id",
            "evidence_id",
            "version_id",
            "passage_id",
            "quote_text",
            "created_by",
        }
    )

    @validates(
        "target_assertion_id",
        "evidence_id",
        "version_id",
        "passage_id",
        "quote_text",
        "created_by",
    )
    def _validate_immutable_binding(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # id-based guard: once persisted, any change from the loaded state is rejected
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new citation")
        return value

    target_assertion_id: Mapped[str] = mapped_column(
        ForeignKey("assertions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="被引用主张（CD-4 Assertion，统一 target）",
    )
    evidence_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidences.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="直接证据边（CD-3；Frozen Lineage §2.3 保留）",
    )
    version_id: Mapped[str | None] = mapped_column(
        ForeignKey("versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="固定版本引用（CD-2 pinned version，I2 — 不随 latest 漂移）",
    )
    passage_id: Mapped[str | None] = mapped_column(
        ForeignKey("passages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="文本定位（CD-2 Passage）",
    )
    quote_text: Mapped[str | None] = mapped_column(Text, nullable=True, comment="引用时的佐证原文")
    note: Mapped[str | None] = mapped_column(Text, nullable=True, comment="考证评注（可变）")
    created_by: Mapped[str | None] = mapped_column(
        String(36), nullable=True, comment="provenance 录入者引用占位（无 User FK — Auth 红线）"
    )
