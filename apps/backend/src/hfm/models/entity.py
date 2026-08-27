"""Entity + EntityType models (CD-1 — ADAPT/REUSE).

ADAPT of HFB `models/academic_relation.py` (AcademicEntity/AcademicEntityType,
CA-001) and `models/graph.py` (GRAPH_ENTITY_TYPES, CA-002) @ `03755b5`:
  - retained: typed-entity pattern (entity_type + name + description);
  - removed: medical-specific HFB types (meridian/disease/technique/
    herb/prescription/symptom/syndrome — G1 boundary) and graph-table
    coupling;
  - rewritten: HFM canonical EntityType families (person/work/place/
    institution/concept/acupoint/event); typed columns only — no
    catch-all JSON schema (§13).
"""

from __future__ import annotations

import enum

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class EntityType(enum.StrEnum):
    """Canonical HFM entity families (Frozen Canonical Model §1)."""

    person = "person"
    work = "work"
    place = "place"
    institution = "institution"
    concept = "concept"
    acupoint = "acupoint"
    event = "event"


_ENTITY_TYPE_VALUES = ", ".join(f"'{t.value}'" for t in EntityType)


class Entity(BaseModel):
    """A typed entity with a stable identity (I5)."""

    __tablename__ = "entities"
    __table_args__ = (
        CheckConstraint(
            f"entity_type IN ({_ENTITY_TYPE_VALUES})",
            name="ck_entities_entity_type",
        ),
    )

    entity_type: Mapped[EntityType] = mapped_column(
        String(30), nullable=False, comment="实体类型（Frozen 7 族）"
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False, comment="实体名称")
    name_zh: Mapped[str | None] = mapped_column(String(300), nullable=True, comment="中文名")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="定义与说明")
