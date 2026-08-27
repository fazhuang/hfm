"""SourceRef model (CD-0 — REUSE/EXTEND).

REUSE of HFB `models/academic_evidence.py::SourceRef` (CA-020) @ `03755b5`
(title/author/edition_info/url), EXTENDed with:
  - a required FK to the immutable `Source` identity (I1 provenance seed);
  - a structured `locator` JSON column (Locator value object) replacing the
    unstructured `page_location` string.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class SourceRef(BaseModel):
    """A physical/editorial reference anchored to an immutable Source."""

    __tablename__ = "source_refs"

    source_id: Mapped[str] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="所属不可变 Source 身份（I1）",
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="物理书名/文献名/论文名"
    )
    author: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="作者/编校者")
    edition_info: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="版本信息/出版社/刊刻年代"
    )
    url: Mapped[str | None] = mapped_column(
        String(1000), nullable=True, comment="数字化链接/古籍库链接"
    )
    locator: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, comment="结构化 Locator（Locator.model_dump(exclude_none=True)）"
    )
