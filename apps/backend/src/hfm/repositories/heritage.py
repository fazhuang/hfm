"""D-domain repository (P1-06 — heritage projects + lineage relations).

Validates the typed-Entity backbone for projects and the person/institution
subject binding (P1-03 reuse); lineage relations reject self-links and
require a resolvable evidence anchor (P1-02) when evidence is provided.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from hfm.models.entity import Entity, EntityType
from hfm.models.evidence import Evidence
from hfm.models.heritage import HeritageProject, HeritageRelation
from hfm.models.person import Person
from hfm.repositories.base import BaseRepository


class HeritageProjectRepository(BaseRepository[HeritageProject]):
    """CRUD for heritage projects with typed-Entity validation (I5)."""

    model = HeritageProject

    async def create(self, **kwargs: Any) -> HeritageProject:
        entity_id = kwargs.get("entity_id")
        if entity_id is None:
            raise ValueError("heritage project entity_id is required")
        entity = await self.session.get(Entity, str(entity_id))
        if entity is None:
            raise ValueError("heritage project entity does not exist")
        if entity.entity_type != EntityType.concept.value:
            raise ValueError("heritage project entity must have entity_type='concept'")
        project_name = str(kwargs.get("project_name") or "")
        if not project_name:
            raise ValueError("heritage project_name is required")
        return await super().create(**kwargs)

    async def get_by_entity_id(self, entity_id: str) -> HeritageProject | None:
        stmt = select(HeritageProject).where(HeritageProject.entity_id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, project_name: str) -> list[HeritageProject]:
        stmt = select(HeritageProject).where(HeritageProject.project_name == project_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class HeritageRelationRepository(BaseRepository[HeritageRelation]):
    """CRUD for heritage lineage relations (evidence-bound, no self-link)."""

    model = HeritageRelation

    async def _validate_subject(self, subject_entity_id: str) -> None:
        """The lineage subject must be a Person (P1-03) or institution Entity."""
        entity = await self.session.get(Entity, subject_entity_id)
        if entity is None:
            raise ValueError(
                f"heritage relation subject entity does not exist: {subject_entity_id}"
            )
        if entity.entity_type == EntityType.person.value:
            person = await self.session.execute(
                select(Person).where(Person.entity_id == subject_entity_id)
            )
            if person.scalar_one_or_none() is None:
                raise ValueError(
                    "heritage relation subject person row does not exist (P1-03 integration)"
                )
        elif entity.entity_type != EntityType.institution.value:
            raise ValueError("heritage relation subject must be a person or institution Entity")

    async def create(self, **kwargs: Any) -> HeritageRelation:
        project_id = str(kwargs.get("project_entity_id") or "")
        subject_id = str(kwargs.get("subject_entity_id") or "")
        if project_id == subject_id:
            raise ValueError("heritage relation cannot link a project to itself")
        project = await HeritageProjectRepository(self.session).get_by_entity_id(project_id)
        if project is None:
            raise ValueError(f"heritage project does not exist: {project_id}")
        await self._validate_subject(subject_id)
        evidence_id = kwargs.get("evidence_id")
        if evidence_id is not None:
            evidence = await self.session.get(Evidence, str(evidence_id))
            if evidence is None:
                raise ValueError("heritage relation evidence does not exist")
        return await super().create(**kwargs)

    async def by_project(self, project_entity_id: str) -> list[HeritageRelation]:
        stmt = select(HeritageRelation).where(
            HeritageRelation.project_entity_id == project_entity_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
