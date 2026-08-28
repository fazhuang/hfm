"""Edition model (CD-2 — REUSE, CA-008).

REUSE of HFB `models/bibliographic.py::Edition` @ `03755b5` (work_id,
edition_name, era, publisher_block, preface_postscript,
lineage_parent_edition_id self-FK).
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class Edition(BaseModel):
    """A specific expression/edition of a Work (宋本、四库本...)."""

    __tablename__ = "editions"

    work_id: Mapped[str] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属 Work",
    )
    edition_name: Mapped[str] = mapped_column(String(500), nullable=False, comment="版本名称")
    era: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="刊刻/抄写年代")
    publisher_block: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="刻板/藏版机构"
    )
    preface_postscript: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="序跋考证信息"
    )
    lineage_parent_edition_id: Mapped[str | None] = mapped_column(
        ForeignKey("editions.id", ondelete="SET NULL"),
        nullable=True,
        comment="版本源流父版本（自引用）",
    )
