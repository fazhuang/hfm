"""Source identity model (CD-0 — ADAPT).

ADAPT of HFB `SourceAdmissionEntry` identity/rights metadata (CA-019) @
`03755b5`:
  - retained: immutable source identity (source_key), source_type,
    source_uri, rights metadata (rights_basis / allowed_scope /
    authorization_basis), legacy source key;
  - removed: the three-tier admission state machine and review workflow
    (governance layer — out of Core Domain);
  - rewritten: HFM-native fields; `source_key` is the unique immutable
    identity (I5); no public-display state (G2/G4 boundary).
"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class Source(BaseModel):
    """An immutable source identity with minimal rights metadata.

    The source_key is the stable external identity (I5); a source is never
    silently overwritten (I4). Admission/publication semantics are handled
    by the governance layer, not this model.
    """

    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("source_key", name="uq_sources_source_key"),)

    #: source_key is a stable identity and must never be mutated (I5).
    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "source_key"})

    @validates("source_key")
    def _validate_source_key(self, key: str, value: object) -> object:
        if value is None:
            raise ValueError("source_key is required")
        current = getattr(self, "source_key", None)
        if current is not None and current != value:
            raise ValueError("source_key is immutable (I5)")
        return value

    source_key: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="不可变来源身份键（唯一）"
    )
    source_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="来源类型（如 古籍/文献/实物/现代论著）"
    )
    source_uri: Mapped[str | None] = mapped_column(
        String(1000), nullable=True, comment="来源 URI/链接"
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="来源标题")
    rights_basis: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="权利依据")
    allowed_scope: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="允许使用范围（ACL 元数据）"
    )
    authorization_basis: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="授权依据说明"
    )
    legacy_source_key: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="HFB 旧数据来源键（迁移用）"
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="撤回时间（Lineage §2.5：撤回 → Evidence taint → Citation 拒绝）",
    )
