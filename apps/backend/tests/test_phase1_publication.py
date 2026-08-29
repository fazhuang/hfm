"""Phase 1 P1-09 — publication workflow tests (review/approve/publish/withdraw).

Admission (P1-01) ≠ approval ≠ published ≠ withdrawn; public visibility is
solely PUBLISHED; unauthorized actions rejected; SoD reviewer != creator;
withdrawal does not destroy history; invalid transitions fail closed.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import (
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
)
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
    from sqlalchemy import select

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


async def _admitted_artifact(session: AsyncSession) -> ContentArtifact:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"pub-src-{id(session)}", title="史料"
    )
    return await ContentArtifactRepository(session).submit_with_source_check(
        source_id=source.id,
        content=b"publishable content",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )


async def test_full_lifecycle_review_approve_publish_withdraw(session: AsyncSession) -> None:
    researcher = await _principal(session, "r1", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "rev1", UserRoleCode.CONTENT_REVIEWER)
    artifact = await _admitted_artifact(session)
    svc = PublicationService(session)
    record = await svc.submit_for_review(artifact_id=artifact.id, creator=researcher)
    assert record.publication_status == PublicationStatus.PENDING_REVIEW.value
    assert not await svc.is_public(artifact.id)

    await svc.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    assert (await svc._record(artifact.id)).publication_status == PublicationStatus.APPROVED.value

    await svc.publish(artifact_id=artifact.id, actor=reviewer)
    assert await svc.is_public(artifact.id)
    assert (await svc._record(artifact.id)).published_at is not None

    await svc.withdraw(artifact_id=artifact.id, actor=reviewer)
    assert not await svc.is_public(artifact.id)  # public visibility ceases
    record = await svc._record(artifact.id)
    assert record.publication_status == PublicationStatus.WITHDRAWN.value
    assert record.withdrawn_at is not None

    await svc.rollback(artifact_id=artifact.id, actor=reviewer)
    assert await svc.is_public(artifact.id)


async def test_admission_alone_does_not_publish(session: AsyncSession) -> None:
    artifact = await _admitted_artifact(session)
    svc = PublicationService(session)
    assert not await svc.is_public(artifact.id)  # admitted ≠ published


async def test_invalid_transition_rejected(session: AsyncSession) -> None:
    researcher = await _principal(session, "r2", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "rev2", UserRoleCode.CONTENT_REVIEWER)
    artifact = await _admitted_artifact(session)
    svc = PublicationService(session)
    await svc.submit_for_review(artifact_id=artifact.id, creator=researcher)
    with pytest.raises(ValueError, match="invalid publication transition"):
        await svc.publish(
            artifact_id=artifact.id, actor=reviewer
        )  # PENDING_REVIEW → PUBLISHED invalid
    with pytest.raises(ValueError, match="invalid publication transition"):
        await svc.withdraw(
            artifact_id=artifact.id, actor=reviewer
        )  # PENDING_REVIEW → WITHDRAWN invalid


async def test_unauthorized_publication_rejected(session: AsyncSession) -> None:
    researcher = await _principal(session, "r3", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "rev3", UserRoleCode.CONTENT_REVIEWER)
    artifact = await _admitted_artifact(session)
    svc = PublicationService(session)
    await svc.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await svc.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    with pytest.raises(PermissionError, match="content:publish"):
        await svc.publish(artifact_id=artifact.id, actor=researcher)  # scholar lacks publish


async def test_unauthorized_withdraw_rejected(session: AsyncSession) -> None:
    researcher = await _principal(session, "r4", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "rev4", UserRoleCode.CONTENT_REVIEWER)
    artifact = await _admitted_artifact(session)
    svc = PublicationService(session)
    await svc.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await svc.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await svc.publish(artifact_id=artifact.id, actor=reviewer)
    with pytest.raises(PermissionError, match="content:withdraw"):
        await svc.withdraw(artifact_id=artifact.id, actor=researcher)


async def test_separation_of_duties(session: AsyncSession) -> None:
    """ADR-07 Guard-02: reviewer must differ from creator (self-review blocked)."""
    await ensure_roles_seeded(session)
    from sqlalchemy import select as _select

    dual = User(username="dual", password_hash=hash_password("pw"))
    session.add(dual)
    await session.flush()
    for role_code in (UserRoleCode.SCHOLAR_RESEARCHER, UserRoleCode.CONTENT_REVIEWER):
        role_row = (
            await session.execute(_select(Role).where(Role.code == role_code.value))
        ).scalar_one()
        await session.execute(user_roles.insert().values(user_id=dual.id, role_id=role_row.id))
    await session.flush()
    token = issue_token(dual.id, UserRoleCode.CONTENT_REVIEWER.value, dual.token_version)
    reviewer = await principal_for_token(session, token)
    assert reviewer.has_permission("content:review") and reviewer.has_permission("assertion:create")
    artifact = await _admitted_artifact(session)
    svc = PublicationService(session)
    await svc.submit_for_review(artifact_id=artifact.id, creator=reviewer)
    with pytest.raises(PermissionError, match="separation of duties"):
        await svc.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)


async def test_only_admitted_content_submittable(session: AsyncSession) -> None:
    researcher = await _principal(session, "r5", UserRoleCode.SCHOLAR_RESEARCHER)
    source, _ = await SourceRepository(session).create_idempotent(source_key="s6", title="史料")
    artifact = await ContentArtifactRepository(session).submit_with_source_check(
        source_id=source.id, content=b"x", rights_status=RightsStatus.UNKNOWN
    )
    assert artifact.admission_state == "rejected"
    svc = PublicationService(session)
    with pytest.raises(ValueError, match="only admitted content"):
        await svc.submit_for_review(artifact_id=artifact.id, creator=researcher)
