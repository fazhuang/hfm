"""Work model (CD-2 — REUSE, CA-007).

REUSE of HFB `models/bibliographic.py::Work` @ `03755b5` (title, dynasty,
composition years, category, is_extant, description). ADAPT: author is an
HFM Entity (author_entity_id FK → entities.id, CD-1) instead of the HFB
person FK.
"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class Work(BaseModel):
    """A FRBR work (《针灸甲乙经》《玄晏春秋》...)."""

    __tablename__ = "works"

    title: Mapped[str] = mapped_column(String(500), nullable=False, comment="著作标题")
    author_entity_id: Mapped[str | None] = mapped_column(
        ForeignKey("entities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="作者（CD-1 Entity，type=person）",
    )
    dynasty: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="朝代")
    composition_year_start: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="成书起始年"
    )
    composition_year_end: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="成书结束年"
    )
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="如 医学/针灸、史部/纪传"
    )
    is_extant: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="是否传世全书（佚书为 false）",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
