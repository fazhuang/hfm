"""Chapter model (CD-2 — REUSE, CA-014).

REUSE of HFB `models/chapter.py::Chapter` @ `03755b5` (title, order,
description, parent_id self-FK hierarchy). ADAPT: anchored to Work
(work_id) since Book is outside CD-2 scope.
"""

from __future__ import annotations

from typing import ClassVar

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class Chapter(BaseModel):
    """A chapter / section within a Work."""

    __tablename__ = "chapters"

    #: hierarchy parent is a protected structural identity relationship.
    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "parent_id"})

    @validates("parent_id")
    def _validate_parent(self, key: str, value: object) -> object:
        if value is not None:
            current_id = getattr(self, "id", None)
            if current_id is not None and value == current_id:
                raise ValueError("parent_id cannot reference the chapter itself")
        return value

    work_id: Mapped[str] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属 Work",
    )
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=True,
        comment="父章节 ID（自引用层级）",
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, comment="章节标题")
    order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False, comment="排序"
    )
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True, comment="章节说明")
