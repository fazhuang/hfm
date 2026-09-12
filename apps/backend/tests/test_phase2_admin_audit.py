# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""Phase-2 P2-02 backend audit integration evidence (P1-03 correction).

Proves the real backend audit append for admin publication actions:
the same service path the admin endpoints exercise (PublicationService
review/publish/withdraw) mutates the publication record AND persists an
immutable audit entry (actor, action, target, timestamp) — not a
frontend-only mocked fetch. Authorization is enforced at the backend
(deny-by-default, ADR-07).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.audit import AuditLog
from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.models.publication import PublicationStatus
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.publication import PublicationService
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.source import SourceRepository


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


async def _admitted_artifact(session: AsyncSession, key: str) -> str:
    source, _ = await SourceRepository(session).create_idempotent(source_key=key, title="史料")
    artifact = await ContentArtifactRepository(session).submit_with_source_check(
        source_id=source.id,
        content=b"publishable content",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    return str(artifact.id)


async def _audit_actions(session: AsyncSession, target_id: str) -> list[str]:
    rows = (
        (
            await session.execute(
                select(AuditLog)
                .where(AuditLog.target_id == target_id)
                .order_by(AuditLog.created_at)
            )
        )
        .scalars()
        .all()
    )
    return [f"{row.actor_id}:{row.action}" for row in rows]


@pytest_asyncio.fixture
async def service(session: AsyncSession) -> AsyncGenerator[PublicationService, None]:
    yield PublicationService(session)


async def test_publish_append_real_audit_record(
    session: AsyncSession, service: PublicationService
) -> None:
    """Publish via the real backend path persists an audit entry with actor,
    action, target and timestamp (P1-03)."""
    researcher = await _principal(session, "researcher-p", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "reviewer-p", UserRoleCode.CONTENT_REVIEWER)
    artifact_id = await _admitted_artifact(session, f"audit-pub-{id(session)}")

    await service.submit_for_review(artifact_id=artifact_id, creator=researcher)
    await service.review(artifact_id=artifact_id, reviewer=reviewer, approve=True)
    published = await service.publish(artifact_id=artifact_id, actor=reviewer)

    assert published.publication_status == PublicationStatus.PUBLISHED.value
    actions = await _audit_actions(session, artifact_id)
    publish_entries = [a for a in actions if a.endswith(":publication.publish")]
    assert len(publish_entries) == 1
    assert publish_entries[0].startswith(reviewer.user_id or "none")

    log_rows = (
        (await session.execute(select(AuditLog).where(AuditLog.target_id == artifact_id)))
        .scalars()
        .all()
    )
    assert all(row.created_at is not None for row in log_rows)


async def test_withdraw_append_real_audit_record(
    session: AsyncSession, service: PublicationService
) -> None:
    """Withdraw via the real backend path persists an audit entry."""
    researcher = await _principal(session, "researcher-w", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "reviewer-w", UserRoleCode.CONTENT_REVIEWER)
    artifact_id = await _admitted_artifact(session, f"audit-wd-{id(session)}")

    await service.submit_for_review(artifact_id=artifact_id, creator=researcher)
    await service.review(artifact_id=artifact_id, reviewer=reviewer, approve=True)
    await service.publish(artifact_id=artifact_id, actor=reviewer)
    withdrawn = await service.withdraw(artifact_id=artifact_id, actor=reviewer)

    assert withdrawn.publication_status == PublicationStatus.WITHDRAWN.value
    actions = await _audit_actions(session, artifact_id)
    assert sum(1 for a in actions if a.endswith(":publication.withdraw")) == 1


async def test_audit_authorization_deny_by_default(
    session: AsyncSession, service: PublicationService
) -> None:
    """A researcher (no content:publish permission) cannot publish; the backend
    denies before any audit append (ADR-07 deny-by-default)."""
    researcher = await _principal(session, "researcher-x", UserRoleCode.SCHOLAR_RESEARCHER)
    artifact_id = await _admitted_artifact(session, f"audit-auth-{id(session)}")
    await service.submit_for_review(artifact_id=artifact_id, creator=researcher)

    with pytest.raises(PermissionError):
        await service.publish(artifact_id=artifact_id, actor=researcher)

    actions = await _audit_actions(session, artifact_id)
    assert not any(a.endswith(":publication.publish") for a in actions)


async def test_audit_record_immutable_append_only(
    session: AsyncSession, service: PublicationService
) -> None:
    """The persisted audit journal is append-only: mutating a loaded entry is
    rejected (I4)."""
    researcher = await _principal(session, "researcher-i", UserRoleCode.SCHOLAR_RESEARCHER)
    artifact_id = await _admitted_artifact(session, f"audit-immu-{id(session)}")
    await service.submit_for_review(artifact_id=artifact_id, creator=researcher)

    log_row = (
        (await session.execute(select(AuditLog).where(AuditLog.target_id == artifact_id)))
        .scalars()
        .first()
    )
    assert log_row is not None  # submit path created an entry

    with pytest.raises(ValueError):
        log_row.detail = "tampered"
    await session.rollback()
