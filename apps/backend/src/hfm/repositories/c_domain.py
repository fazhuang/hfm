"""C-domain repository (P1-05 — typed-Entity terms + evidenced relations).

Validates the typed-Entity backbone (entity_type must be concept/acupoint
for a C-domain term) and the evidence anchor before persistence; relations
reject self-links and unknown targets (fail-closed).
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from hfm.models.c_domain import CDomainRelation, CDomainTerm
from hfm.models.entity import Entity, EntityType
from hfm.models.evidence import Evidence
from hfm.repositories.base import BaseRepository

_C_ENTITY_TYPES = {EntityType.concept.value, EntityType.acupoint.value}


class CDomainTermRepository(BaseRepository[CDomainTerm]):
    """CRUD for C-domain terms with typed-Entity validation (I5)."""

    model = CDomainTerm

    async def create(self, **kwargs: Any) -> CDomainTerm:
        entity_id = kwargs.get("entity_id")
        if entity_id is None:
            raise ValueError("c-domain term entity_id is required")
        entity = await self.session.get(Entity, str(entity_id))
        if entity is None:
            raise ValueError("c-domain term entity does not exist")
        if entity.entity_type not in _C_ENTITY_TYPES:
            raise ValueError("c-domain term entity must have entity_type='concept' or 'acupoint'")
        term_name = str(kwargs.get("term_name") or "")
        if not term_name:
            raise ValueError("c-domain term_name is required")
        return await super().create(**kwargs)

    async def get_by_entity_id(self, entity_id: str) -> CDomainTerm | None:
        stmt = select(CDomainTerm).where(CDomainTerm.entity_id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, term_name: str) -> list[CDomainTerm]:
        stmt = select(CDomainTerm).where(CDomainTerm.term_name == term_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CDomainRelationRepository(BaseRepository[CDomainRelation]):
    """CRUD for C-domain historical relations (evidence-bound, no self-link)."""

    model = CDomainRelation

    async def _validate_targets(
        self, source_term_entity_id: str, target_term_entity_id: str
    ) -> None:
        if source_term_entity_id == target_term_entity_id:
            raise ValueError("c-domain relation cannot link a term to itself")
        for term_id in (source_term_entity_id, target_term_entity_id):
            term = await CDomainTermRepository(self.session).get_by_entity_id(term_id)
            if term is None:
                raise ValueError(f"c-domain term does not exist: {term_id}")
            if term.entity_id != str(term_id):
                raise ValueError("c-domain relation must target the term's entity_id")

    async def create(self, **kwargs: Any) -> CDomainRelation:
        source = str(kwargs.get("source_term_entity_id") or "")
        target = str(kwargs.get("target_term_entity_id") or "")
        await self._validate_targets(source, target)
        evidence_id = kwargs.get("evidence_id")
        if evidence_id is not None:
            evidence = await self.session.get(Evidence, str(evidence_id))
            if evidence is None:
                raise ValueError("c-domain relation evidence does not exist")
        return await super().create(**kwargs)

    async def by_term(self, entity_id: str) -> list[CDomainRelation]:
        """All relations incident to a term (as source or target)."""
        stmt = select(CDomainRelation).where(
            (CDomainRelation.source_term_entity_id == entity_id)
            | (CDomainRelation.target_term_entity_id == entity_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
