"""PublicationRecord model (P1-09 — review/approve/publish/withdraw).

The publication state boundary is distinct from content admission (P1-01):
content exists/admitted ≠ approved ≠ published ≠ withdrawn. Public
visibility is defined solely by publication_status == PUBLISHED.

Lifecycle (frozen acceptance contract): PENDING_REVIEW → APPROVED →
PUBLISHED → WITHDRAWN (rollback → PUBLISHED); invalid transitions fail
closed. Review enforces separation of duties (reviewer != creator, ADR-07
Guard-02). Withdrawal does not destroy provenance/history (audit fields).
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import ClassVar

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class PublicationStatus(enum.StrEnum):
    """Publication lifecycle states (NOT admission states — P1-01 distinct)."""

    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    WITHDRAWN = "WITHDRAWN"


_STATUS_VALUES = ", ".join(f"'{s.value}'" for s in PublicationStatus)

#: allowed transitions (from → to)
ALLOWED_TRANSITIONS: dict[PublicationStatus, frozenset[PublicationStatus]] = {
    PublicationStatus.PENDING_REVIEW: frozenset(
        {PublicationStatus.APPROVED, PublicationStatus.REJECTED}
    ),
    PublicationStatus.APPROVED: frozenset({PublicationStatus.PUBLISHED}),
    PublicationStatus.REJECTED: frozenset(),
    PublicationStatus.PUBLISHED: frozenset({PublicationStatus.WITHDRAWN}),
    PublicationStatus.WITHDRAWN: frozenset({PublicationStatus.PUBLISHED}),  # rollback
}


class PublicationRecord(BaseModel):
    """Publication projection/state for an admitted content artifact."""

    __tablename__ = "publication_records"
    __table_args__ = (
        UniqueConstraint("artifact_id", name="uq_publication_records_artifact"),
        CheckConstraint(
            f"publication_status IN ({_STATUS_VALUES})",
            name="ck_publication_records_status",
        ),
    )

    #: artifact/creator binding is immutable; the lifecycle status and review
    #: audit fields are state-machine mutable through the publication service.
    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "artifact_id", "creator_id"})

    @validates("artifact_id", "creator_id")
    def _validate_immutable_binding(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new publication record")
        return value

    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("content_artifacts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="被发布内容（须先 ADMITTED — P1-01 边界）",
    )
    publication_status: Mapped[PublicationStatus] = mapped_column(
        String(30),
        nullable=False,
        default=PublicationStatus.PENDING_REVIEW,
        server_default="PENDING_REVIEW",
        comment="发布状态（≠ 准入状态）",
    )
    creator_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="提交人（SCHOLAR_RESEARCHER 等）",
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="审核人（CONTENT_REVIEWER；SoD: reviewed_by != creator_id）",
    )
    review_decision: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="approve/reject 决定"
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="审核时间"
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="发布时间"
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="撤回时间"
    )
