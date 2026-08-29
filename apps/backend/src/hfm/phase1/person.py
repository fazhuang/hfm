"""A-domain person service (P1-03 — 皇甫谧人物体系, E-03).

Implements the frozen P1-03 acceptance criterion: person/event records
expose evidence and publication state; no unsupported biography claim is
treated as authoritative; no implicit publication; public visibility is
defined solely by the canonical P1-09 publication state of an admitted
ContentArtifact bound to the person's Entity identity (AB-03/AB-07 — no
parallel publication truth store).

Biographical facts are canonical CD-4 Assertions (subject = the person's
Entity) with Evidence linkage; life events are CD-6 Events related through
EventRelation (person ↔ event) — the canonical person architecture, not a
parallel content system. Mutation endpoints require P1-10 authorization
(default deny).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.hashing import canonical_json
from hfm.models.assertion import Assertion, AssertionType, Confidence, EditorialStatus
from hfm.models.content_artifact import (
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
)
from hfm.models.entity import Entity, EntityType
from hfm.models.event import Event, EventBoundPrecision
from hfm.models.event_relation import EventRelation, EventRelationRole
from hfm.models.person import Person
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.phase1.auth import Principal
from hfm.phase1.version_audit import AuditService
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.event import EventRepository
from hfm.repositories.event_relation import EventRelationRepository

PERMISSION_ASSERTION_CREATE = "assertion:create"


@dataclass(frozen=True)
class PersonView:
    """Serializable person projection (public = evidenced, published only)."""

    entity_id: str
    name_zh: str | None
    name_pinyin: str | None
    courtesy_name: str | None
    pseudonym: str | None
    dynasty: str | None
    publication_status: str
    assertions: tuple[dict[str, Any], ...]
    events: tuple[dict[str, Any], ...]


class PersonService:
    """Canonical A-domain records with evidence + publication state."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------- mutations
    async def create_person(
        self,
        *,
        principal: Principal,
        name_zh: str | None = None,
        name_pinyin: str | None = None,
        courtesy_name: str | None = None,
        pseudonym: str | None = None,
        dynasty: str | None = None,
    ) -> Person:
        """Create a canonical person (Entity(person) + Person row).

        Requires assertion:create; never creates a publication record
        (no implicit publication — P1-09 boundary).
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        if not name_zh and not name_pinyin:
            raise ValueError("person requires a name (name_zh or name_pinyin)")
        entity = Entity(
            entity_type=EntityType.person.value,
            name=str(name_zh or name_pinyin),
            name_zh=name_zh,
        )
        self.session.add(entity)
        await self.session.flush()
        person = Person(
            entity_id=entity.id,
            name_zh=name_zh,
            name_pinyin=name_pinyin,
            courtesy_name=courtesy_name,
            pseudonym=pseudonym,
            dynasty=dynasty,
        )
        self.session.add(person)
        await self.session.flush()
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="person.create",
            target_type="person",
            target_id=person.entity_id,
            detail=canonical_json(
                {"name_zh": name_zh, "name_pinyin": name_pinyin, "dynasty": dynasty}
            ),
        )
        return person

    async def add_biographical_assertion(
        self,
        *,
        principal: Principal,
        person_entity_id: str,
        predicate: str,
        value: str | None = None,
        object_entity_id: str | None = None,
        evidence_ids: tuple[str, ...] = (),
        confidence: str = "medium",
        assertion_type: str = "biographical",
    ) -> Assertion:
        """Add an evidenced biographical claim about the person (I3/I4)."""
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        await self._require_person(person_entity_id)
        if not predicate:
            raise ValueError("assertion predicate is required")
        if not value and not object_entity_id:
            raise ValueError("assertion must carry a literal value or an object entity")
        assertion = await AssertionRepository(self.session).create(
            subject_entity_id=person_entity_id,
            predicate=predicate,
            value=value,
            object_entity_id=object_entity_id,
            assertion_type=AssertionType(assertion_type).value,
            confidence=Confidence(confidence).value,
            created_by=principal.user_id,
        )
        for evidence_id in evidence_ids:
            await AssertionRepository(self.session).attach_evidence(assertion.id, evidence_id)
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="assertion.create",
            target_type="assertion",
            target_id=assertion.id,
            detail=canonical_json({"subject_entity_id": person_entity_id, "predicate": predicate}),
        )
        return assertion

    async def create_event(
        self,
        *,
        principal: Principal,
        person_entity_id: str,
        event_type: str,
        start_year: int | None = None,
        start_month: int | None = None,
        start_day: int | None = None,
        start_precision: str = "unknown",
        start_approximate: bool = False,
        end_year: int | None = None,
        end_month: int | None = None,
        end_day: int | None = None,
        end_precision: str = "unknown",
        end_approximate: bool = False,
        role: str = "actor",
    ) -> Event:
        """Create a 生平事件 (CD-6 Event) and relate it to the person."""
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        await self._require_person(person_entity_id)
        entity = Entity(
            entity_type=EntityType.event.value,
            name=f"{event_type}",
            name_zh=f"{event_type}",
        )
        self.session.add(entity)
        await self.session.flush()
        event = await EventRepository(self.session).create(
            entity_id=entity.id,
            event_type=event_type,
            start_year=start_year,
            start_month=start_month,
            start_day=start_day,
            start_precision=EventBoundPrecision(start_precision).value,
            start_approximate=start_approximate,
            end_year=end_year,
            end_month=end_month,
            end_day=end_day,
            end_precision=EventBoundPrecision(end_precision).value,
            end_approximate=end_approximate,
        )
        relation = await EventRelationRepository(self.session).create(
            entity_id=person_entity_id,
            event_id=event.entity_id,
            relation_role=EventRelationRole(role).value,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="event.create",
            target_type="event",
            target_id=event.entity_id,
            detail=canonical_json(
                {"person_entity_id": person_entity_id, "role": relation.relation_role}
            ),
        )
        return event

    async def relate_event(
        self,
        *,
        principal: Principal,
        person_entity_id: str,
        event_entity_id: str,
        role: str = "participant",
        description: str | None = None,
    ) -> EventRelation:
        """Relate an existing event to the person (person ↔ event relation)."""
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        await self._require_person(person_entity_id)
        relation = await EventRelationRepository(self.session).create(
            entity_id=person_entity_id,
            event_id=event_entity_id,
            relation_role=EventRelationRole(role).value,
            description=description,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="event_relation.create",
            target_type="event_relation",
            target_id=relation.id,
            detail=canonical_json(
                {"person_entity_id": person_entity_id, "event_id": event_entity_id}
            ),
        )
        return relation

    async def admit_person_artifact(
        self,
        *,
        principal: Principal,
        person_entity_id: str,
        source_id: str,
        content: bytes,
        rights_status: RightsStatus,
        provenance_status: ProvenanceStatus = ProvenanceStatus.PENDING,
        format: str | None = None,
        version_id: str | None = None,
    ) -> ContentArtifact:
        """Admit a canonical representation of the person (P1-01 gate).

        The admitted artifact is bound to the person's Entity identity so
        the P1-09 publication state projects onto the person record.
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        await self._require_person(person_entity_id)
        artifact = await ContentArtifactRepository(self.session).submit_with_source_check(
            source_id=source_id,
            content=content,
            format=format,
            provenance_status=provenance_status,
            rights_status=rights_status,
            version_id=version_id,
            subject_entity_id=person_entity_id,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="artifact.submit",
            target_type="content_artifact",
            target_id=artifact.id,
            detail=canonical_json({"person_entity_id": person_entity_id}),
        )
        return artifact

    # ------------------------------------------------------------ visibility
    async def public_visibility(self, person_entity_id: str) -> bool:
        """Person is public iff a PUBLISHED artifact is bound to the entity."""
        return await self._published_subject_entity(person_entity_id) is not None

    async def get_public_person(self, person_entity_id: str) -> dict[str, Any] | None:
        """Public projection: only PUBLISHED persons (evidenced assertions)."""
        person = await self._person_entity(person_entity_id)
        if person is None:
            return None
        if not await self.public_visibility(person_entity_id):
            return None
        view = await self._view(person_entity_id, public_only=True)
        return {
            "entity_id": view.entity_id,
            "name_zh": view.name_zh,
            "name_pinyin": view.name_pinyin,
            "courtesy_name": view.courtesy_name,
            "pseudonym": view.pseudonym,
            "dynasty": view.dynasty,
            "publication_status": view.publication_status,
            "assertions": list(view.assertions),
            "events": list(view.events),
        }

    async def get_research_person(self, person_entity_id: str) -> dict[str, Any]:
        """Research projection: full record incl. evidence + publication state."""
        if await self._person_entity(person_entity_id) is None:
            raise ValueError("person does not exist")
        view = await self._view(person_entity_id, public_only=False)
        return {
            "entity_id": view.entity_id,
            "name_zh": view.name_zh,
            "name_pinyin": view.name_pinyin,
            "courtesy_name": view.courtesy_name,
            "pseudonym": view.pseudonym,
            "dynasty": view.dynasty,
            "publication_status": view.publication_status,
            "assertions": list(view.assertions),
            "events": list(view.events),
        }

    async def list_public_persons(self, query: str | None = None) -> list[dict[str, Any]]:
        """Published persons (P1-08 search integration, public predicate)."""
        published = PublicationStatus.PUBLISHED.value
        published_subjects = select(ContentArtifact.subject_entity_id).where(
            ContentArtifact.subject_entity_id.is_not(None),
            ContentArtifact.id.in_(
                select(PublicationRecord.artifact_id).where(
                    PublicationRecord.publication_status == published
                )
            ),
        )
        base = select(Person).where(Person.entity_id.in_(published_subjects))
        if query:
            pattern = f"%{query}%"
            base = base.where(
                (Person.name_zh.is_not(None) & Person.name_zh.ilike(pattern))
                | (Person.name_pinyin.is_not(None) & Person.name_pinyin.ilike(pattern))
            )
        persons = (await self.session.execute(base.order_by(Person.name_zh))).scalars().all()
        result: list[dict[str, Any]] = []
        for person in persons:
            view = await self._view(person.entity_id, public_only=True)
            result.append(
                {
                    "entity_id": view.entity_id,
                    "name_zh": view.name_zh,
                    "name_pinyin": view.name_pinyin,
                    "dynasty": view.dynasty,
                    "publication_status": view.publication_status,
                }
            )
        return result

    # -------------------------------------------------------------- internals
    async def _view(self, person_entity_id: str, *, public_only: bool) -> PersonView:
        person = await self._person_entity(person_entity_id)
        assert person is not None
        status = await self._publication_status(person_entity_id)
        assertions = (
            (
                await self.session.execute(
                    select(Assertion)
                    .where(Assertion.subject_entity_id == person_entity_id)
                    .order_by(Assertion.created_at)
                )
            )
            .scalars()
            .all()
        )
        public_assertions: list[dict[str, Any]] = []
        for assertion in assertions:
            if public_only and assertion.editorial_status == EditorialStatus.withdrawn.value:
                continue  # public projection: withdrawn claims excluded
            evidence_ids = await AssertionRepository(self.session).get_evidence_ids(assertion.id)
            if public_only and not evidence_ids:
                continue  # every public claim must be evidenced (E-03)
            public_assertions.append(
                {
                    "id": assertion.id,
                    "predicate": assertion.predicate,
                    "value": assertion.value,
                    "object_entity_id": assertion.object_entity_id,
                    "editorial_status": assertion.editorial_status,
                    "confidence": assertion.confidence,
                    "evidence_ids": evidence_ids,
                }
            )
        relations = (
            (
                await self.session.execute(
                    select(EventRelation).where(EventRelation.entity_id == person_entity_id)
                )
            )
            .scalars()
            .all()
        )
        events = [
            {
                "event_id": relation.event_id,
                "role": relation.relation_role,
                "description": relation.description,
            }
            for relation in relations
        ]
        return PersonView(
            entity_id=person.entity_id,
            name_zh=person.name_zh,
            name_pinyin=person.name_pinyin,
            courtesy_name=person.courtesy_name,
            pseudonym=person.pseudonym,
            dynasty=person.dynasty,
            publication_status=status,
            assertions=tuple(public_assertions),
            events=tuple(events),
        )

    async def _person_entity(self, person_entity_id: str) -> Person | None:
        stmt = select(Person).where(Person.entity_id == person_entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _require_person(self, person_entity_id: str) -> None:
        if await self._person_entity(person_entity_id) is None:
            raise ValueError("person does not exist")

    async def _published_subject_entity(self, person_entity_id: str) -> str | None:
        published = PublicationStatus.PUBLISHED.value
        stmt = (
            select(ContentArtifact.id)
            .join(
                PublicationRecord,
                PublicationRecord.artifact_id == ContentArtifact.id,
            )
            .where(
                ContentArtifact.subject_entity_id == person_entity_id,
                PublicationRecord.publication_status == published,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _publication_status(self, person_entity_id: str) -> str:
        published = PublicationStatus.PUBLISHED.value
        pending = PublicationStatus.PENDING_REVIEW.value
        approved = PublicationStatus.APPROVED.value
        withdrawn = PublicationStatus.WITHDRAWN.value
        stmt = (
            select(PublicationRecord.publication_status)
            .join(ContentArtifact, ContentArtifact.id == PublicationRecord.artifact_id)
            .where(ContentArtifact.subject_entity_id == person_entity_id)
            .order_by(PublicationRecord.updated_at.desc())
            .limit(1)
        )
        status = (await self.session.execute(stmt)).scalar_one_or_none()
        if status is None:
            return "UNPUBLISHED"
        if status in (published, pending, approved, withdrawn):
            return str(status)
        return "UNPUBLISHED"

    def _require_permission(self, principal: Principal, code: str) -> None:
        if not principal.is_authenticated or not principal.has_permission(code):
            raise PermissionError(f"missing permission: {code}")


async def published_entity_ids(session: AsyncSession) -> set[str]:
    """Entity ids with a PUBLISHED artifact binding (search predicate input)."""
    published = PublicationStatus.PUBLISHED.value
    stmt = select(ContentArtifact.subject_entity_id).where(
        ContentArtifact.subject_entity_id.is_not(None),
        ContentArtifact.id.in_(
            select(PublicationRecord.artifact_id).where(
                PublicationRecord.publication_status == published
            )
        ),
    )
    result = await session.execute(stmt)
    return {str(v) for v in result.scalars().all() if v is not None}
