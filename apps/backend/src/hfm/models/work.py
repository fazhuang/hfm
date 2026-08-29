"""Work model (CD-2 — REUSE, CA-007).

REUSE of HFB `models/bibliographic.py::Work` @ `03755b5` (title, dynasty,
composition years, category, is_extant, description). ADAPT: author is an
HFM Entity (author_entity_id FK → entities.id, CD-1) instead of the HFB
person FK. P1-04 (frontier-3): optional typed-Entity stable identity
(entity_id 1:1 → entities.id, EntityType.work, I5) matching the
persons/events backbone — the canonical publication projection for a Work
binds to this identity through an admitted ContentArtifact (AB-07).
"""

from __future__ import annotations

from typing import ClassVar

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class Work(BaseModel):
    """A FRBR work (《针灸甲乙经》《玄晏春秋》...)."""

    __tablename__ = "works"
    __table_args__ = (UniqueConstraint("entity_id", name="uq_works_entity_id"),)

    #: structural identity binding is protected (I5/I4).
    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "entity_id"})

    @validates("entity_id")
    def _validate_entity_id(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError("entity_id is immutable (I4): create a new work")
        return value

    title: Mapped[str] = mapped_column(String(500), nullable=False, comment="著作标题")
    entity_id: Mapped[str | None] = mapped_column(
        ForeignKey("entities.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
        comment="P1-04: 稳定标识（= entities.id，1:1 UNIQUE；EntityType.work，I5）",
    )
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
