"""Assertion repository (CD-4, I3/I4 + evidence relations)."""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy import CursorResult, delete, select

from hfm.models.assertion import Assertion, assertion_evidences
from hfm.models.evidence import Evidence
from hfm.repositories.base import BaseRepository


class AssertionRepository(BaseRepository[Assertion]):
    """CRUD for Assertion with coexistence / no-overwrite / evidence relations."""

    model = Assertion

    async def create(self, **kwargs: Any) -> Assertion:
        subject_entity_id = kwargs.get("subject_entity_id")
        value = kwargs.get("value")
        object_entity_id = kwargs.get("object_entity_id")
        if subject_entity_id is None:
            raise ValueError("assertion subject_entity_id is required (I5)")
        if value is None and object_entity_id is None:
            raise ValueError("assertion must carry a literal value or an object entity")
        return await super().create(**kwargs)

    async def attach_evidence(self, assertion_id: str, evidence_id: str) -> bool:
        """Associate an Evidence with an Assertion (M:N, no overwrite of others)."""
        assertion = await self.get_by_id(assertion_id)
        if assertion is None:
            raise ValueError("assertion does not exist")
        evidence = await self.session.get(Evidence, evidence_id)
        if evidence is None:
            raise ValueError("evidence does not exist")
        existing = await self.session.execute(
            select(assertion_evidences.c.assertion_id).where(
                assertion_evidences.c.assertion_id == assertion_id,
                assertion_evidences.c.evidence_id == evidence_id,
            )
        )
        if existing.first() is not None:
            return False  # duplicate relation is a no-op
        await self.session.execute(
            assertion_evidences.insert().values(assertion_id=assertion_id, evidence_id=evidence_id)
        )
        await self.session.flush()
        return True

    async def detach_evidence(self, assertion_id: str, evidence_id: str) -> bool:
        """Remove an Evidence relation (explicit contract operation)."""
        result = cast(
            CursorResult[Any],
            await self.session.execute(
                delete(assertion_evidences).where(
                    assertion_evidences.c.assertion_id == assertion_id,
                    assertion_evidences.c.evidence_id == evidence_id,
                )
            ),
        )
        await self.session.flush()
        return result.rowcount > 0

    async def get_by_subject(self, subject_entity_id: str) -> list[Assertion]:
        stmt = select(Assertion).where(Assertion.subject_entity_id == subject_entity_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_evidence_ids(self, assertion_id: str) -> list[str]:
        stmt = select(assertion_evidences.c.evidence_id).where(
            assertion_evidences.c.assertion_id == assertion_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
