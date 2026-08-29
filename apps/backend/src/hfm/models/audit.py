"""Audit log model (P1-13 — append-only governed-state journal).

Records governed state changes (admission decisions, publication transitions,
domain record creation, reconciliation runs) as immutable, append-only
entries. Preservation of provenance/history is structural: no update or
delete path exists for audit rows (I4); repositories reject any mutation of
audit fields.
"""

from __future__ import annotations

from typing import ClassVar

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class AuditLog(BaseModel):
    """One immutable audit entry for a governed state change (P1-13)."""

    __tablename__ = "audit_log"
    __table_args__ = (
        CheckConstraint("length(action) > 0", name="ck_audit_log_action_present"),
        CheckConstraint("length(target_type) > 0", name="ck_audit_log_target_type_present"),
        CheckConstraint("length(target_id) > 0", name="ck_audit_log_target_id_present"),
    )

    #: every content field is immutable — the journal is append-only (I4).
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {"id", "actor_id", "action", "target_type", "target_id", "detail"}
    )

    @validates("actor_id", "action", "target_type", "target_id", "detail")
    def _validate_immutable(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # id-based guard: once persisted, any change from the loaded state is
        # rejected — audit history is preserved, never rewritten (I4).
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): audit log is append-only")
        return value

    actor_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="操作者（users.id；系统动作可为 NULL）",
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="动作（person.create / publication.publish …）"
    )
    target_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="目标类型（person/work/assertion/…）"
    )
    target_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True, comment="目标 ID"
    )
    detail: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="JSON 摘要（before/after 等）"
    )
