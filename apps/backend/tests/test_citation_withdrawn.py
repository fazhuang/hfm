"""Withdrawn-reference gate tests (CD-5, DAG gate: 撤回引用)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.assertion import EditorialStatus
from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.entity import EntityRepository


async def _make_withdrawn_assertion(session: AsyncSession) -> str:
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    repo = AssertionRepository(session)
    assertion = await repo.create(subject_entity_id=entity.id, predicate="born_in", value="旧说")
    await repo.update(assertion.id, editorial_status=EditorialStatus.withdrawn)
    return assertion.id


async def test_citation_withdrawn_assertion_rejected(session: AsyncSession) -> None:
    """A new citation cannot target a withdrawn assertion (撤回引用 gate)."""
    withdrawn_id = await _make_withdrawn_assertion(session)
    repo = CitationRepository(session)
    with pytest.raises(ValueError):
        await repo.create(target_assertion_id=withdrawn_id, quote_text="撤回后引用")


async def test_citation_active_assertion_allowed(session: AsyncSession) -> None:
    """Active assertions remain citable."""
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="张仲景")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="authored", value="伤寒杂病论"
    )
    repo = CitationRepository(session)
    citation = await repo.create(target_assertion_id=assertion.id, quote_text="伤寒论序")
    assert citation.target_assertion_id == assertion.id


async def test_citation_withdrawn_version_rejected(session: AsyncSession) -> None:
    """I2: new citations cannot pin a withdrawn Version (Frozen Canonical §2)."""
    import pytest

    from hfm.models.entity import EntityType as _ET
    from hfm.repositories.chapter import ChapterRepository
    from hfm.repositories.edition import EditionRepository
    from hfm.repositories.passage import PassageRepository
    from hfm.repositories.version import VersionRepository
    from hfm.repositories.work import WorkRepository

    entity = await EntityRepository(session).create(entity_type=_ET.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="authored", value="针灸甲乙经"
    )
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    version = await VersionRepository(session).create(edition_id=edition.id, version_name="北宋本")
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    passage = await PassageRepository(session).create(chapter_id=chapter.id, content_text="条文")
    await VersionRepository(session).mark_withdrawn(version.id)
    repo = CitationRepository(session)
    with pytest.raises(ValueError):
        await repo.create(
            target_assertion_id=assertion.id, version_id=version.id, passage_id=passage.id
        )


async def test_citation_tainted_evidence_rejected(session: AsyncSession) -> None:
    """Lineage §2.5: withdrawn Source → tainted Evidence → new Citation rejected."""
    import pytest

    from hfm.repositories.evidence import EvidenceRepository
    from hfm.repositories.source import SourceRepository
    from hfm.repositories.source_ref import SourceRefRepository

    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="born_in", value="安定"
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="withdraw-src", title="旧史"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="旧史")
    evidence = await EvidenceRepository(session).create(description="旧证", source_ref_id=ref.id)
    await AssertionRepository(session).attach_evidence(assertion.id, evidence.id)
    # withdraw the source → cascade taints the evidence
    await SourceRepository(session).mark_withdrawn(source.id, reason="考订有误")
    reloaded = await EvidenceRepository(session).get_by_id(evidence.id)
    assert reloaded is not None
    assert reloaded.taint_status == "source_withdrawn"
    repo = CitationRepository(session)
    with pytest.raises(ValueError):
        await repo.create(target_assertion_id=assertion.id, quote_text="引用污损证据")
