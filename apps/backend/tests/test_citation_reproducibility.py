"""I2 Version Reproducibility for Citation (CD-5 — pinned reference, no latest drift)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.edition import EditionRepository
from hfm.repositories.entity import EntityRepository
from hfm.repositories.passage import PassageRepository
from hfm.repositories.version import VersionRepository
from hfm.repositories.work import WorkRepository


async def _make_pinned_context(session: AsyncSession) -> tuple[str, str, str]:
    """Build assertion + text chain; return (assertion, version, passage) ids."""
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="authored", value="针灸甲乙经"
    )
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    version_v1 = await VersionRepository(session).create(
        edition_id=edition.id, version_name="北宋本"
    )
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    passage = await PassageRepository(session).create(
        chapter_id=chapter.id, version_id=version_v1.id, content_text="凡刺之要"
    )
    return assertion.id, version_v1.id, passage.id


async def test_i2_citation_pinned_version_no_latest_drift(session: AsyncSession) -> None:
    """I2: a citation pinned to V1 stays on V1 after V2 is created."""
    target, v1_id, passage_id = await _make_pinned_context(session)
    repo = CitationRepository(session)
    citation = await repo.create(
        target_assertion_id=target, version_id=v1_id, passage_id=passage_id, quote_text="定本引文"
    )
    assert citation.version_id == v1_id
    # create a newer version under the same edition
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="四库本")
    await VersionRepository(session).create(edition_id=edition.id, version_name="四库全书本")
    # reload the citation — it still resolves V1 (no silent latest substitution)
    reloaded = await repo.get_by_id(citation.id)
    assert reloaded is not None
    assert reloaded.version_id == v1_id
    assert reloaded.passage_id == passage_id


async def test_i2_citation_version_pin_immutable(session: AsyncSession) -> None:
    """I2: the pinned version binding cannot be rewritten post-create."""
    target, v1_id, passage_id = await _make_pinned_context(session)
    repo = CitationRepository(session)
    citation = await repo.create(
        target_assertion_id=target, version_id=v1_id, passage_id=passage_id
    )
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="校本")
    v2 = await VersionRepository(session).create(edition_id=edition.id, version_name="校本版")
    with pytest.raises(ValueError):
        await repo.update(citation.id, version_id=v2.id)
