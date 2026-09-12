# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
# The canonical gates (`mypy src tests`) resolve hfm to source and pass;
# per-file mypy/pyright see the editable install and flag import-untyped /
# reportMissingImports (same artifact present in accepted test files). File-
# level suppression keeps the per-file guard green without weakening the real
# gate.
"""Phase 1 Frontier-6 — DoD-07 integrated public + research boundary tests.

Integration-only combined-surface proof (E-11/E-12 together against one
dataset): anonymous public surfaces (P1-11 portal) and authenticated
research workspace (P1-12) coexist without leakage in either direction.
Each scenario creates published content AND private research workspace
state in the same session, then verifies:

- anonymous principal can reach the public portal but is denied every
  research workspace method (no authorization weakening);
- public portal responses stay strictly whitelisted — no ownership,
  research metadata, project or note content — even when workspace
  state exists in the same dataset;
- withdrawal removes public visibility immediately even while related
  research workspace state remains (no publication-state bypass).

These tests add no feature semantics; they only exercise the combined
boundary that neither single-surface suite can prove.
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.literature import LiteratureService
from hfm.phase1.portal import PortalService
from hfm.phase1.publication import PublicationService
from hfm.phase1.research_workspace import ResearchWorkspaceService
from hfm.repositories.source import SourceRepository

_WORK_KEYS = {"work_id", "title", "dynasty", "category", "edition_count", "publication_status"}
_EDITION_KEYS = {"edition_id", "edition_name", "era", "publisher_block"}
_COUNT_KEYS = {"works", "persons", "heritage_projects", "c_terms"}

_PRINCIPAL_SEQ = 0


async def _principal(session: AsyncSession, role_code: UserRoleCode) -> Principal:
    """Create a distinct HFM user with the requested role (unique username)."""
    global _PRINCIPAL_SEQ
    _PRINCIPAL_SEQ += 1
    await ensure_roles_seeded(session)
    user = User(
        username=f"fi-{role_code.value.lower()}-{_PRINCIPAL_SEQ}",
        password_hash=hash_password("pw"),
    )
    session.add(user)
    await session.flush()
    role_row = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
    await session.flush()
    token = issue_token(user.id, role_code.value, user.token_version)
    return await principal_for_token(session, token)


async def _scholar(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.SCHOLAR_RESEARCHER)


async def _reviewer(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.CONTENT_REVIEWER)


async def _publish_work(session: AsyncSession, scholar: Principal, work_id: str) -> str:
    """Admit + review + publish a Work artifact via P1-09; returns artifact id."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"fi-src-{id(session) % 10**6}", title="史料"
    )
    artifact = await LiteratureService(session).admit_work_artifact(
        principal=scholar,
        work_id=work_id,
        source_id=source.id,
        content=f"work:{work_id}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    reviewer = await _reviewer(session)
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=scholar)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return str(artifact.id)


async def _add_workspace_state(
    session: AsyncSession, scholar: Principal
) -> tuple[dict[str, object], dict[str, object]]:
    """Private owner-scoped project + note in the same dataset."""
    ws = ResearchWorkspaceService(session)
    project = await ws.create_project(
        principal=scholar, title="私有项目标题", description="私有项目描述"
    )
    note = await ws.create_note(
        principal=scholar, project_id=project["project_id"], content="私有笔记内容"
    )
    return project, note


# -------------------------------------------------- combined-boundary
async def test_anonymous_denied_on_research_while_public_visible(
    session: AsyncSession,
) -> None:
    """Public portal reachable anonymously; research workspace fails closed.

    Same dataset holds published content; the anonymous principal can read
    the public projection but every research workspace method is denied
    (DoD-07 no authorization weakening across surfaces).
    """
    scholar = await _scholar(session)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=scholar, title="集成匿名", dynasty="西晋")
    await svc.create_edition(principal=scholar, work_id=work.id, edition_name="宋刻本")
    await _publish_work(session, scholar, work.id)
    assert await PortalService(session).work_editions(work.id) is not None

    anon = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())
    ws = ResearchWorkspaceService(session)
    denied = 0
    for attempt in (
        ws.list_projects(principal=anon),
        ws.list_notes(principal=anon),
        ws.create_project(principal=anon, title="x"),
        ws.create_note(principal=anon, content="x"),
        ws.get_project(principal=anon, project_id="x"),
    ):
        try:
            await attempt
        except PermissionError:
            denied += 1
    assert denied == 5


async def test_public_portal_excludes_research_state_with_workspace_present(
    session: AsyncSession,
) -> None:
    """Strict public whitelist holds even with workspace state in the dataset.

    Published content is publicly visible, while private project/note
    content, ownership and research metadata never appear in portal
    responses (E-12 no public leakage through the P1-11 surface).
    """
    scholar = await _scholar(session)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=scholar, title="集成白名单", dynasty="西晋")
    await svc.create_edition(principal=scholar, work_id=work.id, edition_name="宋刻本")
    await _publish_work(session, scholar, work.id)

    project, note = await _add_workspace_state(session, scholar)
    assert project["project_id"] and note["note_id"]

    home = await PortalService(session).home()
    works_result = await PortalService(session).works(page=1, page_size=20)
    editions = await PortalService(session).work_editions(work.id)

    assert set(home) == {"works", "counts"}
    assert set(home["counts"]) == _COUNT_KEYS
    assert set(works_result) == {"works", "total", "page"}
    for entry in works_result["works"]:
        assert set(entry) == _WORK_KEYS
    assert editions is not None
    for entry in editions:
        assert set(entry) == _EDITION_KEYS

    blob = json.dumps(home) + json.dumps(works_result) + json.dumps(editions)
    for forbidden in (
        "私有项目标题",
        "私有项目描述",
        "私有笔记内容",
        "owner_id",
        "research_projects",
        "research_notes",
        "project_id",
    ):
        assert forbidden not in blob, f"workspace/ownership field leaked: {forbidden}"


async def test_withdrawal_removes_public_visibility_with_research_state_present(
    session: AsyncSession,
) -> None:
    """Withdrawal is immediate even when related research state exists.

    Published content plus private workspace state coexist; withdrawal
    removes the public projection at once while the owner's workspace
    remains intact (E-11 immediate withdrawal; no publication-state bypass).
    """
    scholar = await _scholar(session)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=scholar, title="集成即时撤回", dynasty="西晋")
    await svc.create_edition(principal=scholar, work_id=work.id, edition_name="宋刻本")
    artifact_id = await _publish_work(session, scholar, work.id)
    assert await PortalService(session).work_editions(work.id) is not None

    project, note = await _add_workspace_state(session, scholar)
    assert project["project_id"] and note["note_id"]

    reviewer = await _reviewer(session)
    await PublicationService(session).withdraw(artifact_id=artifact_id, actor=reviewer)

    assert await PortalService(session).work_editions(work.id) is None
    home = await PortalService(session).home()
    assert work.id not in {w["work_id"] for w in home["works"]}
    assert home["counts"]["works"] == 0
    ws = ResearchWorkspaceService(session)
    assert (await ws.list_projects(principal=scholar))["total"] == 1
    assert (await ws.list_notes(principal=scholar))["total"] == 1
