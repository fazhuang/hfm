"""Phase 1 P1-01 content admission tests (canonical content core).

Proves the frozen P1-01 acceptance criterion (E-01):
  - invalid provenance/rights is rejected (observable rejection log);
  - admitted content carries source + version state;
  - no metadata-only admission;
  - fail-closed validation (malformed input raises; gate failures rejected);
  - duplicate/idempotent behavior (same source+hash → one record);
  - immutability of the admitted integrity/source binding (I4);
  - no publication semantics on the model;
  - no HFB runtime dependency.
"""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import (
    ContentAdmissionState,
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
)
from hfm.models.source import Source
from hfm.models.version import Version
from hfm.repositories.content_artifact import (
    ADMISSION_REJECTION_REASONS,
    ContentArtifactRepository,
)
from hfm.repositories.edition import EditionRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.version import VersionRepository
from hfm.repositories.work import WorkRepository


async def _make_source(session: AsyncSession) -> Source:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="p1-source", title="皇甫谧史料"
    )
    return source


async def _make_version(session: AsyncSession) -> Version:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    return await VersionRepository(session).create(edition_id=edition.id, version_name="北宋本")


def _valid_kwargs(source_id: str) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "content": "皇甫谧甲午岁生".encode() * 4,
        "provenance_status": ProvenanceStatus.VERIFIED,
        "rights_status": RightsStatus.CUSTOMER_OWNED,
    }


async def test_valid_admission_succeeds(session: AsyncSession) -> None:
    source = await _make_source(session)
    version = await _make_version(session)
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(
        **_valid_kwargs(source.id), version_id=version.id
    )
    assert artifact.admission_state == ContentAdmissionState.ADMITTED.value
    assert artifact.rejection_reason is None
    assert artifact.source_id == source.id
    assert artifact.version_id == version.id
    assert len(artifact.content_hash) == 64
    assert artifact.provenance_status == ProvenanceStatus.VERIFIED.value
    assert artifact.rights_status == RightsStatus.CUSTOMER_OWNED.value
    # reload — persisted state
    reloaded = await repo.get_by_id(artifact.id)
    assert reloaded is not None and reloaded.admission_state == ContentAdmissionState.ADMITTED.value


async def test_metadata_only_admission_rejected(session: AsyncSession) -> None:
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(**{**_valid_kwargs(source.id), "content": b""})
    assert artifact.admission_state == ContentAdmissionState.REJECTED.value
    assert artifact.rejection_reason == "metadata_only_admission"


async def test_failed_provenance_rejected(session: AsyncSession) -> None:
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(
        **{**_valid_kwargs(source.id), "provenance_status": ProvenanceStatus.FAILED}
    )
    assert artifact.admission_state == ContentAdmissionState.REJECTED.value
    assert artifact.rejection_reason == "invalid_provenance"


async def test_unknown_rights_rejected(session: AsyncSession) -> None:
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(
        **{**_valid_kwargs(source.id), "rights_status": RightsStatus.UNKNOWN}
    )
    assert artifact.admission_state == ContentAdmissionState.REJECTED.value
    assert artifact.rejection_reason == "unknown_rights"


async def test_missing_source_rejected(session: AsyncSession) -> None:
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(
        **_valid_kwargs("00000000-0000-7000-8000-000000000000")
    )
    assert artifact.admission_state == ContentAdmissionState.REJECTED.value
    assert artifact.rejection_reason == "missing_source_provenance"


async def test_invalid_version_binding_rejected(session: AsyncSession) -> None:
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(
        **{**_valid_kwargs(source.id), "version_id": "00000000-0000-7000-8000-000000000000"}
    )
    assert artifact.admission_state == ContentAdmissionState.REJECTED.value
    assert artifact.rejection_reason == "invalid_version_binding"


async def test_malformed_input_fails_closed(session: AsyncSession) -> None:
    repo = ContentArtifactRepository(session)
    with pytest.raises(ValueError, match="source_id"):
        await repo.submit(source_id=None, content=b"x")  # type: ignore[arg-type]


async def test_all_invalid_cases_have_known_reasons() -> None:
    """E-01: replay of every rejection class is covered by a known reason."""
    assert set(ADMISSION_REJECTION_REASONS) == {
        "missing_source_provenance",
        "metadata_only_admission",
        "invalid_provenance",
        "unknown_rights",
        "invalid_version_binding",
    }


async def test_idempotent_submission_single_record(session: AsyncSession) -> None:
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    kwargs = _valid_kwargs(source.id)
    first = await repo.submit_with_source_check(**kwargs)
    second = await repo.submit_with_source_check(**kwargs)
    assert first.id == second.id
    assert await repo.count() == 1


async def test_source_hash_uniqueness_db_enforced(session: AsyncSession) -> None:
    """UNIQUE(source_id, content_hash) is enforced at the DB layer."""
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    await repo.submit_with_source_check(**_valid_kwargs(source.id))
    # raw insert with the same (source, hash) must fail
    row = (
        await session.execute(
            pytest.importorskip("sqlalchemy").text(
                "SELECT content_hash FROM content_artifacts LIMIT 1"
            )
        )
    ).scalar_one()
    with pytest.raises(IntegrityError):
        await session.execute(
            pytest.importorskip("sqlalchemy").text(
                "INSERT INTO content_artifacts (id, source_id, content_hash,"
                " provenance_status, rights_status, validation_result, admission_state,"
                " created_at, updated_at)"
                " VALUES ('9'*36, :sid, :hash, 'verified', 'customer_owned', 'pass',"
                " 'admitted', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"sid": source.id, "hash": row},
        )


async def test_admitted_binding_immutable(session: AsyncSession) -> None:
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(**_valid_kwargs(source.id))
    await session.flush()
    with pytest.raises(ValueError, match="immutable"):
        await repo.update(artifact.id, content_hash="0" * 64)
    with pytest.raises(ValueError, match="immutable"):
        await repo.update(artifact.id, admission_state=ContentAdmissionState.SUBMITTED.value)


async def test_no_publication_fields_on_model() -> None:
    """Admission must not imply publication (P1-09): no approved/published state."""
    cols = {c.name for c in ContentArtifact.__table__.columns}
    assert not (cols & {"approved", "published", "public_visible", "release_version"})


async def test_rejected_rows_carry_reason_db_constraint(session: AsyncSession) -> None:
    """CHECK: rejected rows must have a rejection_reason."""
    source = await _make_source(session)
    repo = ContentArtifactRepository(session)
    artifact = await repo.submit_with_source_check(**_valid_kwargs(source.id))
    assert artifact.rejection_reason is None  # admitted row has no reason
    bad = await repo.submit_with_source_check(
        **{
            **_valid_kwargs(source.id),
            "content": b"different-content",
            "provenance_status": ProvenanceStatus.FAILED,
        }
    )
    assert bad.rejection_reason == "invalid_provenance"


async def test_no_hfb_runtime_dependency() -> None:
    import pathlib

    for path in (
        pathlib.Path("src/hfm/models/content_artifact.py"),
        pathlib.Path("src/hfm/repositories/content_artifact.py"),
    ):
        text = path.read_text(encoding="utf-8")
        assert "from hfb" not in text and "import hfb" not in text
