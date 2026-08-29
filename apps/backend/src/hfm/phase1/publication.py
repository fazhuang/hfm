"""Publication workflow service (P1-09 — review/approve/publish/withdraw).

Enforces the frozen publication state boundary: content admitted (P1-01)
≠ approved ≠ published ≠ withdrawn. Public visibility is defined solely by
publication_status == PUBLISHED. Transitions are guarded and fail closed;
review enforces separation of duties (reviewer != creator, ADR-07 Guard-02);
withdrawal does not destroy provenance/history (the record retains audit
fields). RBAC is enforced server-side through the P1-10 principal. Fail-closed
transitions; reviewed_by never equals creator_id. Public visibility is
PUBLISHED only; separation of duties enforced.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ContentAdmissionState, ContentArtifact
from hfm.models.publication import (
    ALLOWED_TRANSITIONS,
    PublicationRecord,
    PublicationStatus,
)
from hfm.phase1.auth import Principal

PERMISSION_REVIEW = "content:review"
PERMISSION_PUBLISH = "content:publish"
PERMISSION_WITHDRAW = "content:withdraw"


class PublicationService:
    """Server-side publication lifecycle (P1-09)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def submit_for_review(self, *, artifact_id: str, creator: Principal) -> PublicationRecord:
        """Creator (researcher) submits an ADMITTED artifact for review."""
        if not creator.is_authenticated or not creator.has_permission("assertion:create"):
            raise PermissionError("submit requires a researcher principal")
        artifact = await self.session.get(ContentArtifact, artifact_id)
        if artifact is None:
            raise ValueError("artifact does not exist")
        if artifact.admission_state != ContentAdmissionState.ADMITTED.value:
            raise ValueError("only admitted content may be submitted for publication")
        existing = (
            await self.session.execute(
                select(PublicationRecord).where(PublicationRecord.artifact_id == artifact_id)
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise ValueError("publication record already exists for this artifact")
        record = PublicationRecord(
            artifact_id=artifact_id,
            publication_status=PublicationStatus.PENDING_REVIEW.value,
            creator_id=creator.user_id or "",
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def _record(self, artifact_id: str) -> PublicationRecord:
        record = (
            await self.session.execute(
                select(PublicationRecord).where(PublicationRecord.artifact_id == artifact_id)
            )
        ).scalar_one_or_none()
        if record is None:
            raise ValueError("publication record does not exist")
        return record

    async def review(
        self, *, artifact_id: str, reviewer: Principal, approve: bool
    ) -> PublicationRecord:
        """CONTENT_REVIEWER approves or rejects (SoD: reviewer != creator)."""
        self._require_permission(reviewer, PERMISSION_REVIEW)
        record = await self._record(artifact_id)
        if record.creator_id == reviewer.user_id:
            raise PermissionError("separation of duties: reviewer must differ from creator")
        self._transition(
            record, PublicationStatus.APPROVED if approve else PublicationStatus.REJECTED
        )
        record.reviewed_by = reviewer.user_id
        record.review_decision = "approve" if approve else "reject"
        record.reviewed_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def publish(self, *, artifact_id: str, actor: Principal) -> PublicationRecord:
        """CONTENT_REVIEWER publishes an APPROVED record (explicit authorization)."""
        self._require_permission(actor, PERMISSION_PUBLISH)
        record = await self._record(artifact_id)
        self._transition(record, PublicationStatus.PUBLISHED)
        record.published_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def withdraw(self, *, artifact_id: str, actor: Principal) -> PublicationRecord:
        """CONTENT_REVIEWER withdraws a PUBLISHED record (public visibility ceases)."""
        self._require_permission(actor, PERMISSION_WITHDRAW)
        record = await self._record(artifact_id)
        self._transition(record, PublicationStatus.WITHDRAWN)
        record.withdrawn_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def rollback(self, *, artifact_id: str, actor: Principal) -> PublicationRecord:
        """Authorized rollback of a WITHDRAWN record back to PUBLISHED."""
        self._require_permission(actor, PERMISSION_PUBLISH)
        record = await self._record(artifact_id)
        self._transition(record, PublicationStatus.PUBLISHED)
        record.withdrawn_at = None
        record.published_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def is_public(self, artifact_id: str) -> bool:
        """Public visibility predicate: only PUBLISHED records are public."""
        record = (
            await self.session.execute(
                select(PublicationRecord).where(PublicationRecord.artifact_id == artifact_id)
            )
        ).scalar_one_or_none()
        return record is not None and record.publication_status == PublicationStatus.PUBLISHED.value

    def _require_permission(self, principal: Principal, code: str) -> None:
        if not principal.is_authenticated or not principal.has_permission(code):
            raise PermissionError(f"missing permission: {code}")

    def _transition(self, record: PublicationRecord, target: PublicationStatus) -> None:
        current = PublicationStatus(record.publication_status)
        allowed = ALLOWED_TRANSITIONS.get(current, frozenset())
        if target not in allowed:
            raise ValueError(f"invalid publication transition: {current.value} → {target.value}")
        record.publication_status = target
