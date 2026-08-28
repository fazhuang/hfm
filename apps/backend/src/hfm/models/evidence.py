"""Evidence model (CD-3 — REUSE, CA-021 + CA-024 + integrity).

REUSE of HFB `models/academic_evidence.py::Evidence` (CA-021) @ `03755b5`:
description / evidence_level (LEVEL_1..4) / source_ref_id / source_passage_id
/ taint lifecycle (CA-024). EXTEND (per Frozen EVIDENCE-LINEAGE §2.6):
  - content_hash integrity column (canonical hash via hfm.core.hashing);
  - DB CHECK: at least one provenance anchor (source_ref_id OR
    source_passage_id) — orphan Evidence is rejected (I1).
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import ClassVar

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class EvidenceLevel(enum.StrEnum):
    """Academic evidence strength levels (REUSE, CA-021)."""

    LEVEL_1 = "LEVEL_1"  # 一手出土文献实物
    LEVEL_2 = "LEVEL_2"  # 传世最早善本/宋刻本
    LEVEL_3 = "LEVEL_3"  # 历代正史/经典医学文献注疏
    LEVEL_4 = "LEVEL_4"  # 现代学术论著/考证推理


class Evidence(BaseModel):
    """An academic argument anchored to a SourceRef and/or an in-system Passage.

    Every Evidence carries at least one provenance anchor (I1); its
    content_hash is a deterministic integrity digest, protected from
    post-create mutation (I4).
    """

    __tablename__ = "evidences"
    __table_args__ = (
        CheckConstraint(
            "source_ref_id IS NOT NULL OR source_passage_id IS NOT NULL",
            name="ck_evidences_provenance_anchor",
        ),
    )

    #: provenance anchors, content, and the derived integrity digest are
    #: protected (I1/I4): content_hash can never go stale because the
    #: covered fields are immutable after creation.
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "id",
            "content_hash",
            "source_ref_id",
            "source_passage_id",
            "description",
            "evidence_level",
        }
    )

    @validates("content_hash")
    def _validate_content_hash(self, key: str, value: object) -> object:
        current = getattr(self, "content_hash", None)
        if current is not None and value != current:
            raise ValueError("content_hash is immutable (I4)")
        return value

    @validates("description")
    def _validate_description(self, key: str, value: object) -> object:
        current = getattr(self, "description", None)
        if current is not None and value != current:
            raise ValueError("description is immutable (I4): create a new evidence instead")
        return value

    @validates("evidence_level")
    def _validate_evidence_level(self, key: str, value: object) -> object:
        current = getattr(self, "evidence_level", None)
        if current is not None and value != current:
            raise ValueError("evidence_level is immutable (I4): create a new evidence instead")
        return value

    description: Mapped[str] = mapped_column(Text, nullable=False, comment="证据内容概述/考证逻辑")
    evidence_level: Mapped[EvidenceLevel] = mapped_column(
        Enum(EvidenceLevel, native_enum=False, length=20),
        nullable=False,
        default=EvidenceLevel.LEVEL_3,
        comment="学术证据力等级",
    )
    source_ref_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_refs.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="物理来源引用（I1 锚点之一）",
    )
    source_passage_id: Mapped[str | None] = mapped_column(
        ForeignKey("passages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="系统内数字文献段落（I1 锚点之一）",
    )
    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="完整性哈希（canonical hash，create 时计算，不可变）",
    )

    # --- taint lifecycle (CA-024 REUSE) ---
    taint_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="clean",
        server_default="clean",
        comment="污损状态: clean|source_withdrawn|quarantined",
    )
    tainted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="污损时间"
    )
    taint_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="污损原因")
