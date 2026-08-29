"""Phase 1 P1-13 — version/audit/reconciliation tests (E-13).

Valid version lineage; invalid predecessor/link rejection; audit record
generation; prohibited destructive mutation rejection; reconciliation PASS
case; reconciliation mismatch fail-closed case; provenance/history
preservation (append-only).
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.models.reconciliation import ReconciliationStatus
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.version_audit import (
    AuditService,
    ReconciliationMismatchError,
    ReconciliationService,
    VersionLineageService,
)
from hfm.repositories.audit import AuditLogRepository
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository
from hfm.repositories.version import VersionRepository
from hfm.repositories.work import WorkRepository


async def _principal(session: AsyncSession, username: str, role_code: UserRoleCode) -> Principal:
    await ensure_roles_seeded(session)
    user = User(username=username, password_hash=hash_password("pw"))
    session.add(user)
    await session.flush()
    role_row = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
    await session.flush()
    token = issue_token(user.id, role_code.value, user.token_version)
    return await principal_for_token(session, token)


async def _lineage(session: AsyncSession) -> tuple[str, str, str]:
    """work → edition → version (root) → version (child); returns ids."""
    from hfm.repositories.edition import EditionRepository

    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    root = await VersionRepository(session).create(edition_id=edition.id, version_name="祖本")
    child = await VersionRepository(session).create(
        edition_id=edition.id, version_name="覆刻本", parent_version_id=root.id
    )
    return root.id, child.id, edition.id


async def test_valid_version_lineage(session: AsyncSession) -> None:
    root_id, child_id, _ = await _lineage(session)
    service = VersionLineageService(session)
    chain = await service.lineage(child_id)
    assert [n.version_id for n in chain] == [child_id, root_id]
    digest = await service.lineage_hash(child_id)
    assert len(digest) == 64
    assert digest == await service.lineage_hash(child_id)  # deterministic
    report = await service.integrity_report()
    assert report["ok"] is True and report["cycles"] == 0 and report["orphan_parents"] == 0


async def test_invalid_predecessor_rejected(session: AsyncSession) -> None:
    root_id, child_id, edition_id = await _lineage(session)
    # orphan parent reference rejected at create-time (fail-closed)
    with pytest.raises(ValueError, match="parent version does not exist"):
        await VersionRepository(session).create(
            edition_id=edition_id,
            version_name="孤儿",
            parent_version_id="00000000-0000-7000-8000-000000000000",
        )
    # broken lineage detection raises (missing version)
    with pytest.raises(ValueError, match="lineage"):
        await VersionLineageService(session).lineage("00000000-0000-7000-8000-000000000000")
    # lineage parent is immutable — cycle formation impossible post-create
    child_stmt = select(VersionRepository.model).where(
        VersionRepository.model.version_name == "覆刻本"
    )
    child = (await session.execute(child_stmt)).scalars().first()
    assert child is not None and child.id == child_id
    with pytest.raises(ValueError, match="immutable"):
        await VersionRepository(session).update(child_id, parent_version_id=None)


async def test_audit_record_generation(session: AsyncSession) -> None:
    admin = await _principal(session, "v1", UserRoleCode.SYSTEM_ADMIN)
    entry = await AuditService(session).record(
        actor_id=admin.user_id,
        action="test.action",
        target_type="widget",
        target_id="w-1",
        detail='{"k": 1}',
    )
    assert entry.action == "test.action"
    recent = await AuditService(session).list_recent(limit=10)
    assert any(e.id == entry.id for e in recent)
    by_target = await AuditService(session).for_target("widget", "w-1")
    assert len(by_target) == 1


async def test_audit_append_only_prohibited_mutation(session: AsyncSession) -> None:
    admin = await _principal(session, "v2", UserRoleCode.SYSTEM_ADMIN)
    entry = await AuditService(session).record(
        actor_id=admin.user_id, action="a.b", target_type="t", target_id="t-1"
    )
    with pytest.raises(ValueError, match="immutable"):
        await AuditLogRepository(session).update(entry.id, action="a.evil")
    with pytest.raises(ValueError, match="immutable"):
        entry.detail = "rewritten"
        await session.flush()
    # provenance/history preserved: the original record is unchanged
    fresh = await AuditLogRepository(session).get_by_id(entry.id)
    assert fresh is not None and fresh.action == "a.b"


async def test_reconciliation_pass_recorded(session: AsyncSession) -> None:
    admin = await _principal(session, "v3", UserRoleCode.SYSTEM_ADMIN)
    _ = await _lineage(session)  # deterministic seed rows (2 versions)
    service = ReconciliationService(session)
    versions = (await session.execute(select(VersionRepository.model))).scalars().all()
    from hfm.core.hashing import calculate_canonical_metadata_sha256

    expected_hash = calculate_canonical_metadata_sha256(sorted(v.id for v in versions))
    run = await service.reconcile(
        scope="table:versions",
        expected_count=len(versions),
        expected_hash=expected_hash,
        created_by=admin.user_id,
    )
    assert run.status == ReconciliationStatus.PASS.value
    assert run.expected_count == run.actual_count
    assert run.expected_hash == run.actual_hash
    latest = await service.latest_for_scope("table:versions")
    assert latest is not None and latest.id == run.id


async def test_reconciliation_mismatch_fail_closed(session: AsyncSession) -> None:
    admin = await _principal(session, "v4", UserRoleCode.SYSTEM_ADMIN)
    _ = await _lineage(session)
    service = ReconciliationService(session)
    # wrong expected metrics → recorded FAIL run + raised error (never WARN-only)
    with pytest.raises(ReconciliationMismatchError, match="FAIL"):
        await service.reconcile(
            scope="table:versions",
            expected_count=999,
            expected_hash="0" * 64,
            created_by=admin.user_id,
        )
    latest = await service.latest_for_scope("table:versions")
    assert latest is not None and latest.status == ReconciliationStatus.FAIL.value
    # the FAIL run is preserved as evidence (no silent completion)


async def test_reconciliation_unknown_scope_rejected(session: AsyncSession) -> None:
    admin = await _principal(session, "v5", UserRoleCode.SYSTEM_ADMIN)
    with pytest.raises(ValueError, match="unknown reconciliation scope"):
        await ReconciliationService(session).reconcile(
            scope="table:does_not_exist",
            expected_count=0,
            expected_hash="0" * 64,
            created_by=admin.user_id,
        )


async def test_batch_scope_reconciliation(session: AsyncSession) -> None:
    """Batch metrics: content_artifacts as the canonical batch table."""
    admin = await _principal(session, "v6", UserRoleCode.SYSTEM_ADMIN)
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"v6-src-{id(session)}", title="史料"
    )
    await ContentArtifactRepository(session).submit_with_source_check(
        source_id=source.id,
        content=b"batch item",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    service = ReconciliationService(session)
    artifacts = (await session.execute(select(ContentArtifactRepository.model))).scalars().all()
    from hfm.core.hashing import calculate_canonical_metadata_sha256

    expected_hash = calculate_canonical_metadata_sha256(sorted(a.id for a in artifacts))
    run = await service.reconcile(
        scope=f"batch:v6-{id(session)}",
        expected_count=len(artifacts),
        expected_hash=expected_hash,
        created_by=admin.user_id,
    )
    assert run.status == ReconciliationStatus.PASS.value


async def test_prohibited_destructive_mutation_rejected(session: AsyncSession) -> None:
    """No silent destructive overwrite of canonical history (I4 guards)."""
    _, child_id, _ = await _lineage(session)
    # evidence content is immutable (revision = new evidence)
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"v7-src-{id(session)}", title="史料"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="引")
    evidence = await EvidenceRepository(session).create(
        description="原始证据", source_ref_id=ref.id
    )
    with pytest.raises(ValueError, match="immutable"):
        await EvidenceRepository(session).update(evidence.id, description="改写历史")
    # version lineage parent cannot be rewritten
    with pytest.raises(ValueError, match="immutable"):
        await VersionRepository(session).update(child_id, parent_version_id=None)
    # reconciliation evidence cannot be amended
    from hfm.core.hashing import calculate_canonical_metadata_sha256

    run = await ReconciliationService(session).reconcile(
        scope="table:passages",
        expected_count=0,
        expected_hash=calculate_canonical_metadata_sha256([]),
    )
    assert run.status == ReconciliationStatus.PASS.value
    with pytest.raises(ValueError, match="immutable"):
        run.status = ReconciliationStatus.FAIL
        await session.flush()


async def test_version_immutability_and_history_preserved(session: AsyncSession) -> None:
    root_id, child_id, _ = await _lineage(session)
    child = await VersionRepository(session).get_by_id(child_id)
    assert child is not None
    # structural identity (parent) is protected via the repository — no
    # silent destructive overwrite of canonical lineage (I4); history kept
    with pytest.raises(ValueError, match="immutable"):
        await VersionRepository(session).update(child_id, parent_version_id=None)
    assert child.parent_version_id == root_id
