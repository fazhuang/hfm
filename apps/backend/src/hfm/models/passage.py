"""Passage model (CD-2 — REUSE, CA-015 + locator).

REUSE of HFB `models/passage.py::Passage` @ `03755b5` (chapter_id,
version_id optional, content_text, translation, notes, order, tags).
Locator reproducibility: a passage's locator is derived from its FK chain
(work → chapter → passage + optional version binding); version_id is a
pinned fixed reference — Core never silently resolves "latest" (I2).
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class Passage(BaseModel):
    """The atomic unit of classical text — independently citable and comparable."""

    __tablename__ = "passages"

    chapter_id: Mapped[str] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属章节 ID",
    )
    version_id: Mapped[str | None] = mapped_column(
        ForeignKey("versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="固定版本绑定（I2 pinned reference，可空）",
    )
    content_text: Mapped[str] = mapped_column(Text, nullable=False, comment="条文正文")
    translation: Mapped[str | None] = mapped_column(Text, nullable=True, comment="现代汉语翻译")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="注释")
    order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False, comment="排序（章节内定位）"
    )
    tags: Mapped[str | None] = mapped_column(
        String(1000), nullable=True, comment="标签（逗号分隔）"
    )
