"""Create the smallest deterministic public record for local recovery.

Source: apps/frontend/src/config/corePerson.ts, whose constants are the
repository's confirmed flagship anchors. This command writes only the
identity/publication chain needed by the real public person API.

Usage from apps/backend:
    HFM_DATABASE_URL=postgresql+asyncpg://... python scripts/bootstrap_recovery.py
"""

from __future__ import annotations

import asyncio
import hashlib

import hfm.models.assertion  # noqa: F401
import hfm.models.audit  # noqa: F401
import hfm.models.c_domain  # noqa: F401
import hfm.models.chapter  # noqa: F401
import hfm.models.citation  # noqa: F401
import hfm.models.edition  # noqa: F401
import hfm.models.event  # noqa: F401
import hfm.models.event_relation  # noqa: F401
import hfm.models.evidence  # noqa: F401
import hfm.models.heritage  # noqa: F401
import hfm.models.institution  # noqa: F401
import hfm.models.passage  # noqa: F401
import hfm.models.reconciliation  # noqa: F401
import hfm.models.research_workspace  # noqa: F401
import hfm.models.source_ref  # noqa: F401
import hfm.models.version  # noqa: F401
import hfm.models.work  # noqa: F401

from hfm.db.session import SessionFactory
from hfm.models.content_artifact import (
    ContentAdmissionState,
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
    ValidationResult,
)
from hfm.models.entity import Entity, EntityType
from hfm.models.identity import User
from hfm.models.person import Person, PersonDomainStatus
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.models.source import Source

ENTITY_ID = "person-huangfu-mi"
PERSON_ID = "00000000-0000-7000-8000-000000000001"
SOURCE_ID = "00000000-0000-7000-8000-000000000002"
PERSON_CONTENT = "HFM recovery foundation: 皇甫谧 | 215—282"


async def bootstrap() -> None:
    async with SessionFactory() as session:
        existing = await session.get(Entity, ENTITY_ID)
        if existing is not None:
            if existing.name != "皇甫谧" or existing.entity_type != EntityType.person.value:
                raise RuntimeError(f"recovery entity {ENTITY_ID} does not match the contract")
            print(f"RECOVERY_BOOTSTRAP=ALREADY_PRESENT entity_id={ENTITY_ID}")
            return

        source = Source(
            id=SOURCE_ID,
            source_key="hfm-recovery/core-person-v1",
            source_type="repository-authoritative-content",
            title="HFM corePerson confirmed flagship anchors",
            rights_basis="repository-authoritative customer-confirmed content",
            allowed_scope="recovery development and runtime smoke",
        )
        entity = Entity(
            id=ENTITY_ID,
            entity_type=EntityType.person.value,
            name="皇甫谧",
            name_zh="皇甫谧",
            description="西晋著名医学家、文学家、史学家，针灸学专著《针灸甲乙经》的编纂者，世称针灸鼻祖。",
        )
        person = Person(
            id=PERSON_ID,
            entity_id=ENTITY_ID,
            name_zh="皇甫谧",
            name_pinyin="Huangfu Mi",
            dynasty="西晋",
            domain_status=PersonDomainStatus.verified.value,
        )
        creator = User(
            username="recovery-bootstrap-creator",
            password_hash="recovery-bootstrap-disabled",
            is_active=False,
        )
        reviewer = User(
            username="recovery-bootstrap-reviewer",
            password_hash="recovery-bootstrap-disabled",
            is_active=False,
        )
        content = PERSON_CONTENT.encode("utf-8")
        session.add_all([source, entity, person, creator, reviewer])
        await session.flush()
        artifact = ContentArtifact(
            source_id=SOURCE_ID,
            content_hash=hashlib.sha256(content).hexdigest(),
            format="text/plain",
            provenance_status=ProvenanceStatus.VERIFIED.value,
            rights_status=RightsStatus.CUSTOMER_OWNED.value,
            validation_result=ValidationResult.PASS.value,
            admission_state=ContentAdmissionState.ADMITTED.value,
            subject_entity_id=ENTITY_ID,
            created_by=creator.id,
        )
        session.add(artifact)
        await session.flush()
        publication = PublicationRecord(
            artifact_id=artifact.id,
            publication_status=PublicationStatus.PUBLISHED.value,
            creator_id=creator.id,
            reviewed_by=reviewer.id,
            review_decision="approve",
        )
        session.add(publication)
        await session.commit()
        print(f"RECOVERY_BOOTSTRAP=CREATED entity_id={ENTITY_ID}")


def main() -> None:
    asyncio.run(bootstrap())


if __name__ == "__main__":
    main()
