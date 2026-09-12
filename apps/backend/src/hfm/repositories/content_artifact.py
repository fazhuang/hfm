"""ContentArtifact repository (P1-01 — fail-closed admission gate).

Implements the frozen P1-01 acceptance criterion:
  - invalid provenance/rights is rejected (rejection recorded with reason);
  - admitted content carries source + version state;
  - no metadata-only admission (content_hash is mandatory);
  - fail-closed validation (malformed input raises; gate failures are
    observable REJECTED records — E-01 rejection log);
  - idempotent admission (same source_id + content_hash maps to one record);
  - no publication implied by admission.
"""

from __future__ import annotations

from sqlalchemy import select

from hfm.core.hashing import calculate_bytes_sha256
from hfm.models.content_artifact import (
    ContentAdmissionState,
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
    ValidationResult,
)
from hfm.models.entity import Entity
from hfm.models.source import Source
from hfm.models.version import Version
from hfm.repositories.base import BaseRepository

ADMISSION_REJECTION_REASONS = (
    "missing_source_provenance",
    "metadata_only_admission",
    "invalid_provenance",
    "unknown_rights",
    "invalid_version_binding",
    "invalid_subject_entity_binding",
)


class ContentArtifactRepository(BaseRepository[ContentArtifact]):
    """CRUD for the canonical content-admission core (P1-01)."""

    model = ContentArtifact

    async def get_by_source_hash(self, source_id: str, content_hash: str) -> ContentArtifact | None:
        stmt = select(ContentArtifact).where(
            ContentArtifact.source_id == source_id,
            ContentArtifact.content_hash == content_hash,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def submit(
        self,
        *,
        source_id: str,
        content: bytes,
        format: str | None = None,
        provenance_status: ProvenanceStatus = ProvenanceStatus.PENDING,
        rights_status: RightsStatus = RightsStatus.UNKNOWN,
        validation_result: ValidationResult = ValidationResult.PENDING,
        version_id: str | None = None,
        subject_entity_id: str | None = None,
        created_by: str | None = None,
    ) -> ContentArtifact:
        """Submit a content item for admission (fail-closed gate).

        Returns the admitted/rejected artifact record; the rejection log is
        the artifact row itself (admission_state=rejected + rejection_reason).
        Idempotent: the same (source_id, content_hash) resolves to one record.
        """
        if source_id is None:
            raise ValueError("admission requires source_id")
        content_hash = calculate_bytes_sha256(content) if content else ""
        existing = await self.get_by_source_hash(source_id, content_hash)
        if existing is not None:
            return existing  # idempotent admission — same logical artifact

        version_reason = await self._version_binding_reason(version_id)
        if version_reason is not None:
            # the attempted Version reference cannot be persisted (FK), so the
            # rejection records the reason with a NULL binding (E-01 log)
            version_id = None
        subject_reason = await self._subject_entity_reason(subject_entity_id)
        if subject_reason is not None:
            subject_entity_id = None
        reason = self._gate_reason(
            source_id=source_id,
            content_hash=content_hash,
            provenance_status=provenance_status,
            rights_status=rights_status,
        )
        if reason is None and version_reason is not None:
            reason = version_reason
        if reason is None and subject_reason is not None:
            reason = subject_reason
        state = (
            ContentAdmissionState.REJECTED if reason is not None else ContentAdmissionState.ADMITTED
        )
        artifact = ContentArtifact(
            source_id=source_id,
            content_hash=content_hash,
            format=format,
            provenance_status=provenance_status.value,
            rights_status=rights_status.value,
            validation_result=validation_result.value,
            admission_state=state.value,
            rejection_reason=reason,
            version_id=version_id,
            subject_entity_id=subject_entity_id,
            created_by=created_by,
        )
        self.session.add(artifact)
        await self.session.flush()
        return artifact

    async def submit_with_source_check(
        self,
        *,
        source_id: str,
        content: bytes,
        format: str | None = None,
        provenance_status: ProvenanceStatus = ProvenanceStatus.PENDING,
        rights_status: RightsStatus = RightsStatus.UNKNOWN,
        validation_result: ValidationResult = ValidationResult.PENDING,
        version_id: str | None = None,
        subject_entity_id: str | None = None,
        created_by: str | None = None,
    ) -> ContentArtifact:
        """Canonical admission entry: verifies the Source row exists first.

        A nonexistent Source (unresolvable provenance) is rejected with
        reason ``missing_source_provenance`` before the gate runs; the
        artifact record is still persisted as the observable rejection log.
        """
        if source_id is None:
            raise ValueError("admission requires source_id")
        source = await self.session.get(Source, source_id)
        if source is None:
            content_hash = calculate_bytes_sha256(content) if content else ""
            artifact = ContentArtifact(
                source_id=None,  # unresolvable provenance cannot reference a Source
                content_hash=content_hash,
                format=format,
                provenance_status=provenance_status.value,
                rights_status=rights_status.value,
                validation_result=validation_result.value,
                admission_state=ContentAdmissionState.REJECTED.value,
                rejection_reason="missing_source_provenance",
                version_id=None,
                subject_entity_id=None,
                created_by=created_by,
            )
            self.session.add(artifact)
            await self.session.flush()
            return artifact
        return await self.submit(
            source_id=source_id,
            content=content,
            format=format,
            provenance_status=provenance_status,
            rights_status=rights_status,
            validation_result=validation_result,
            version_id=version_id,
            subject_entity_id=subject_entity_id,
            created_by=created_by,
        )

    async def _version_binding_reason(self, version_id: str | None) -> str | None:
        """'invalid_version_binding' when the referenced Version does not exist."""
        if version_id is None:
            return None
        version = await self.session.get(Version, version_id)
        if version is None:
            return "invalid_version_binding"
        return None

    async def _subject_entity_reason(self, subject_entity_id: str | None) -> str | None:
        """'invalid_subject_entity_binding' when the bound Entity does not exist.

        Fail-closed (P1-03/P1-04): an admitted artifact may only project a
        canonical domain entity — an unresolvable subject binding is rejected.
        """
        if subject_entity_id is None:
            return None
        entity = await self.session.get(Entity, str(subject_entity_id))
        if entity is None:
            return "invalid_subject_entity_binding"
        return None

    async def get_by_subject_entity(self, subject_entity_id: str) -> list[ContentArtifact]:
        """Artifacts bound to a domain entity (publication projection inputs)."""
        stmt = (
            select(ContentArtifact)
            .where(ContentArtifact.subject_entity_id == subject_entity_id)
            .order_by(ContentArtifact.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def _gate_reason(
        self,
        *,
        source_id: str,
        content_hash: str,
        provenance_status: ProvenanceStatus,
        rights_status: RightsStatus,
    ) -> str | None:
        """Fail-closed admission gate: returns the first rejection reason, or
        None when the item passes into ADMITTED state."""
        if not source_id:
            return "missing_source_provenance"
        if not content_hash:
            return "metadata_only_admission"
        if provenance_status == ProvenanceStatus.FAILED:
            return "invalid_provenance"
        if rights_status == RightsStatus.UNKNOWN:
            return "unknown_rights"
        return None
