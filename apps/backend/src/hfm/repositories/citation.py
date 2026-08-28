"""Citation repository (CD-5, withdrawn gate + immutable binding)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from hfm.models.assertion import EditorialStatus, assertion_evidences
from hfm.models.citation import Citation
from hfm.repositories.base import BaseRepository


class CitationRepository(BaseRepository[Citation]):
    """CRUD for Citation with withdrawn-reference gate and pinned binding."""

    model = Citation

    async def create(self, **kwargs: Any) -> Citation:
        target_assertion_id = kwargs.get("target_assertion_id")
        if target_assertion_id is None:
            raise ValueError("citation target_assertion_id is required")
        # resolve target assertion — withdrawn assertions cannot be newly cited
        from hfm.models.assertion import Assertion

        assertion = await self.session.get(Assertion, str(target_assertion_id))
        if assertion is None:
            raise ValueError("target assertion does not exist")
        if assertion.editorial_status == EditorialStatus.withdrawn:
            raise ValueError("cannot cite a withdrawn assertion (withdrawn-reference gate)")
        # withdrawn-version gate (Frozen Canonical §2 — I2)
        version_id = kwargs.get("version_id")
        if version_id is not None:
            from hfm.models.version import Version

            version = await self.session.get(Version, str(version_id))
            if version is None:
                raise ValueError("pinned version does not exist")
            if version.withdrawn_at is not None:
                raise ValueError("cannot cite a withdrawn version (I2)")
        # tainted-evidence gate (Lineage §2.5: withdrawn Source → tainted Evidence → rejected)
        evidence_ids = await self.get_assertion_evidence_ids(str(target_assertion_id))
        direct_evidence_id = kwargs.get("evidence_id")
        if direct_evidence_id is not None:
            evidence_ids.append(str(direct_evidence_id))
        for evidence_id in evidence_ids:
            from hfm.models.evidence import Evidence

            evidence = await self.session.get(Evidence, evidence_id)
            if evidence is not None and evidence.taint_status != "clean":
                raise ValueError("cannot cite tainted evidence (withdrawn-source cascade)")
        # FK existence for optional pins is enforced by the database (SET NULL / RESTRICT)
        return await super().create(**kwargs)

    async def get_assertion_evidence_ids(self, assertion_id: str) -> list[str]:
        """Evidence ids linked to an assertion (assertion_evidences join)."""
        stmt = select(assertion_evidences.c.evidence_id).where(
            assertion_evidences.c.assertion_id == assertion_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_target_assertion(self, target_assertion_id: str) -> list[Citation]:
        stmt = select(Citation).where(Citation.target_assertion_id == target_assertion_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
