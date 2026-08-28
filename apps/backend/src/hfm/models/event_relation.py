"""EventRelation model (CD-6 — Person/Event 关系, ADAPT of CA-001).

ADAPT of HFB `models/academic_relation.py::AcademicRelation` @ `03755b5`
(source_entity_id / target_entity_id / relation_type / description):
  - retained: typed relation with role + free-text note;
  - removed: medical knowledge-graph coupling (relation_evidences M:N,
    RelationConfidence) — contested roles/claims live in the CD-4 Assertion
    claim layer aggregated to the Event (Assertion Contract §5);
  - rewritten: HFM Person/Event 关系 — CD-1 stable Entity identity on the
    participant side (§17: no second person identifier), Event on the other.

Binding fields (entity_id / event_id / relation_role) are immutable (I4) —
a corrected relation is a new relation; only the note is mutable.
"""

from __future__ import annotations

import enum
from typing import ClassVar

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class EventRelationRole(enum.StrEnum):
    """Participant role in an event (HFM-native; ADAPT of HFB relation_type)."""

    actor = "actor"
    participant = "participant"
    witness = "witness"
    other = "other"


_ROLE_VALUES = ", ".join(f"'{r.value}'" for r in EventRelationRole)


class EventRelation(BaseModel):
    """A Person/Event relation (entity ↔ event) with a typed role."""

    __tablename__ = "event_relations"
    __table_args__ = (
        UniqueConstraint("entity_id", "event_id", "relation_role", name="uq_event_relations"),
        CheckConstraint(
            f"relation_role IN ({_ROLE_VALUES})",
            name="ck_event_relations_role",
        ),
        CheckConstraint(
            "entity_id <> event_id",
            name="ck_event_relations_not_self",
        ),
    )

    #: structural binding is immutable (I4) — a correction is a new relation.
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {"id", "entity_id", "event_id", "relation_role"}
    )

    @validates("entity_id", "event_id", "relation_role")
    def _validate_immutable_binding(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # id-based guard: once persisted, any change from the loaded state is rejected
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new relation")
        return value

    entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="参与者（CD-1 Entity 稳定身份；通常 Person — §17）",
    )
    event_id: Mapped[str] = mapped_column(
        ForeignKey("events.entity_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="事件（= entities.id）",
    )
    relation_role: Mapped[EventRelationRole] = mapped_column(
        String(20),
        nullable=False,
        comment="参与角色: actor/participant/witness/other",
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="关系阐述（可变 note）"
    )
