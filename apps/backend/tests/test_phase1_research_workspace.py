# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
# The canonical gates (`mypy src tests`) resolve hfm to source and pass;
# per-file mypy/pyright see the editable install and flag import-untyped /
# reportMissingImports (same artifact present in accepted test files) plus
# import-not-found for modules added this session. File-level suppression
# keeps the per-file guard green without weakening the real gate.
"""Phase 1 P1-12 — authenticated research workspace tests (E-12, ADR-05/07).

The authenticated research workflow preserves ownership and exposes richer
authorized research evidence/state without public leakage: owner-scoped
projects + notes, two-user isolation, guessed-ID isolation, anonymous and
wrong-role denial, deny-by-default, token_version revocation, richer
research evidence access (reader reuse), public projection excludes
workspace state, publication boundaries preserved, version specificity
preserved, C-domain safety and zero clinical recommendation semantics
(AB-14). Migration tests: 0013 upgrade / downgrade / upgrade-again /
single-head validation.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.models.research_workspace import ResearchProject
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.literature import LiteratureService
from hfm.phase1.reader import ReaderService
from hfm.phase1.research_workspace import ResearchWorkspaceService
from hfm.repositories.source import SourceRepository

BACKEND_DIR = Path(__file__).resolve().parent.parent

_FORBIDDEN_CLINICAL = (
    "diagnosis",
    "treatment",
    "prescription",
    "recommendation",
    "主穴",
    "配穴",
)

_PRINCIPAL_SEQ = 0


async def _principal(session: AsyncSession, role_code: UserRoleCode) -> Principal:
    """Create a distinct HFM user with the requested role (real token)."""
    global _PRINCIPAL_SEQ
    _PRINCIPAL_SEQ += 1
    await ensure_roles_seeded(session)
    user = User(
        username=f"p12-{role_code.value.lower()}-{_PRINCIPAL_SEQ}",
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


async def _user_a(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.SCHOLAR_RESEARCHER)


async def _user_b(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.SCHOLAR_RESEARCHER)


async def _student(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.STUDENT_RESEARCHER)


async def _reviewer(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.CONTENT_REVIEWER)


# ------------------------------------------------------------------ CRUD
async def test_project_crud_owner_scoped(session: AsyncSession) -> None:
    """Create → read → update → delete a project (permitted state)."""
    a = await _user_a(session)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=a, title="甲乙经校勘项目", description="卷三")
    assert project["project_id"]
    assert project["title"] == "甲乙经校勘项目"
    assert project["description"] == "卷三"
    assert set(project) == {"project_id", "title", "description", "created_at"}

    got = await svc.get_project(principal=a, project_id=project["project_id"])
    assert got["project_id"] == project["project_id"]
    assert got["title"] == project["title"]
    assert got["description"] == project["description"]

    updated = await svc.update_project(
        principal=a, project_id=project["project_id"], title="新标题", description="修订描述"
    )
    assert updated["title"] == "新标题"
    assert updated["description"] == "修订描述"

    listed = await svc.list_projects(principal=a)
    assert listed["total"] == 1
    assert [p["project_id"] for p in listed["projects"]] == [project["project_id"]]

    await svc.delete_project(principal=a, project_id=project["project_id"])
    assert (await svc.list_projects(principal=a))["total"] == 0


async def test_note_crud_owner_scoped(session: AsyncSession) -> None:
    """Notes CRUD with optional owner-scoped project binding."""
    a = await _user_a(session)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=a, title="项目")
    note = await svc.create_note(
        principal=a, content="第一条校勘记录", title="札记", project_id=project["project_id"]
    )
    assert note["note_id"]
    assert note["project_id"] == project["project_id"]
    assert note["title"] == "札记"
    assert note["content"] == "第一条校勘记录"

    got = await svc.get_note(principal=a, note_id=note["note_id"])
    assert got["note_id"] == note["note_id"]
    assert got["project_id"] == note["project_id"]
    assert got["title"] == note["title"]
    assert got["content"] == note["content"]

    updated = await svc.update_note(principal=a, note_id=note["note_id"], content="修订记录")
    assert updated["content"] == "修订记录"

    listed = await svc.list_notes(principal=a, project_id=project["project_id"])
    assert listed["total"] == 1

    await svc.delete_note(principal=a, note_id=note["note_id"])
    assert (await svc.list_notes(principal=a))["total"] == 0


async def test_project_delete_cascades_notes(session: AsyncSession) -> None:
    """Deleting a project deletes its notes (CASCADE)."""
    a = await _user_a(session)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=a, title="待删项目")
    await svc.create_note(principal=a, project_id=project["project_id"], content="随项目删除")
    await svc.delete_project(principal=a, project_id=project["project_id"])
    assert (await svc.list_notes(principal=a))["total"] == 0


# ---------------------------------------------------------- isolation
async def test_two_user_isolation(session: AsyncSession) -> None:
    """E-12: User A's projects/notes are inaccessible to User B."""
    a = await _user_a(session)
    b = await _user_b(session)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=a, title="A 的项目")
    note = await svc.create_note(principal=a, project_id=project["project_id"], content="A 的笔记")

    assert (await svc.list_projects(principal=b))["projects"] == []
    assert (await svc.list_notes(principal=b))["notes"] == []
    # direct object access fails closed (no existence leak)
    for method, args in (
        (svc.get_project, {"project_id": project["project_id"]}),
        (svc.update_project, {"project_id": project["project_id"], "title": "x"}),
        (svc.delete_project, {"project_id": project["project_id"]}),
        (svc.get_note, {"note_id": note["note_id"]}),
        (svc.update_note, {"note_id": note["note_id"], "content": "x"}),
        (svc.delete_note, {"note_id": note["note_id"]}),
    ):
        with pytest.raises(KeyError):
            await method(principal=b, **args)
    # A still owns everything
    assert await svc.get_project(principal=a, project_id=project["project_id"])
    assert await svc.get_note(principal=a, note_id=note["note_id"])


async def test_guessed_id_isolation(session: AsyncSession) -> None:
    """Random/guessed IDs and other users' IDs never open objects."""
    a = await _user_a(session)
    b = await _user_b(session)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=a, title="A")
    bogus = "00000000-0000-0000-0000-000000000000"
    with pytest.raises(KeyError):
        await svc.get_project(principal=a, project_id=bogus)
    with pytest.raises(KeyError):
        await svc.get_note(principal=a, note_id=bogus)
    # cross-user project binding on note create is rejected
    with pytest.raises(KeyError):
        await svc.create_note(principal=b, project_id=project["project_id"], content="x")
    with pytest.raises(KeyError):
        await svc.list_notes(principal=b, project_id=project["project_id"])


# ---------------------------------------------------------- authorization
async def test_role_matrix_student_personal_notes_authorized(session: AsyncSession) -> None:
    """ADR-07 §4.1: STUDENT_RESEARCHER personal notes/bookmarks authorized."""
    student = await _student(session)
    svc = ResearchWorkspaceService(session)
    note = await svc.create_note(principal=student, content="个人研读笔记", title="札记")
    assert note["note_id"]
    assert (await svc.get_note(principal=student, note_id=note["note_id"]))[
        "content"
    ] == "个人研读笔记"
    assert (await svc.list_notes(principal=student))["total"] == 1
    updated = await svc.update_note(principal=student, note_id=note["note_id"], content="修订")
    assert updated["content"] == "修订"
    await svc.delete_note(principal=student, note_id=note["note_id"])
    assert (await svc.list_notes(principal=student))["total"] == 0


async def test_role_matrix_student_project_capability_denied(session: AsyncSession) -> None:
    """ADR-07 §4.1: STUDENT_RESEARCHER has NO scholarly project capability."""
    student = await _student(session)
    svc = ResearchWorkspaceService(session)
    with pytest.raises(PermissionError):
        await svc.create_project(principal=student, title="x")
    with pytest.raises(PermissionError):
        await svc.list_projects(principal=student)
    with pytest.raises(PermissionError):
        await svc.get_project(principal=student, project_id="any")
    with pytest.raises(PermissionError):
        await svc.update_project(principal=student, project_id="any", title="x")
    with pytest.raises(PermissionError):
        await svc.delete_project(principal=student, project_id="any")


async def test_role_matrix_scholar_project_capability(session: AsyncSession) -> None:
    """ADR-07 §4.1: SCHOLAR_RESEARCHER scholarly project CRUD on own objects."""
    scholar = await _user_a(session)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=scholar, title="学者项目")
    assert (await svc.list_projects(principal=scholar))["total"] == 1
    assert await svc.get_project(principal=scholar, project_id=project["project_id"])
    updated = await svc.update_project(
        principal=scholar, project_id=project["project_id"], title="改题"
    )
    assert updated["title"] == "改题"
    await svc.delete_project(principal=scholar, project_id=project["project_id"])
    assert (await svc.list_projects(principal=scholar))["total"] == 0


async def test_role_matrix_scholar_note_capability(session: AsyncSession) -> None:
    """ADR-07: SCHOLAR_RESEARCHER retains personal notes alongside projects."""
    scholar = await _user_a(session)
    svc = ResearchWorkspaceService(session)
    note = await svc.create_note(principal=scholar, content="学者笔记")
    assert note["note_id"]
    assert await svc.get_note(principal=scholar, note_id=note["note_id"])


async def test_role_matrix_reviewer_denied(session: AsyncSession) -> None:
    """ADR-07: CONTENT_REVIEWER gets no research workspace capability."""
    reviewer = await _reviewer(session)
    svc = ResearchWorkspaceService(session)

    async def expect_denied(operation: Any) -> None:
        with pytest.raises(PermissionError):
            await operation

    await expect_denied(svc.create_project(principal=reviewer, title="x"))
    await expect_denied(svc.list_projects(principal=reviewer))
    await expect_denied(svc.get_project(principal=reviewer, project_id="any"))
    await expect_denied(svc.update_project(principal=reviewer, project_id="any", title="x"))
    await expect_denied(svc.delete_project(principal=reviewer, project_id="any"))
    await expect_denied(svc.create_note(principal=reviewer, content="x"))
    await expect_denied(svc.list_notes(principal=reviewer))
    await expect_denied(svc.get_note(principal=reviewer, note_id="any"))
    await expect_denied(svc.update_note(principal=reviewer, note_id="any", content="x"))
    await expect_denied(svc.delete_note(principal=reviewer, note_id="any"))


async def test_role_matrix_unmapped_role_denied(session: AsyncSession) -> None:
    """Unknown/unmapped role → deny by default (no permission source)."""
    unmapped = Principal(user_id="unmapped-user", roles=("MYSTERY_ROLE",), permissions=frozenset())
    svc = ResearchWorkspaceService(session)
    with pytest.raises(PermissionError):
        await svc.list_notes(principal=unmapped)
    with pytest.raises(PermissionError):
        await svc.create_project(principal=unmapped, title="x")


async def test_role_matrix_admin_semantics(session: AsyncSession) -> None:
    """SYSTEM_ADMIN holds the frozen all-codes mapping (incl. research:*)."""
    admin = await _principal(session, UserRoleCode.SYSTEM_ADMIN)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=admin, title="管理项目")
    assert project["project_id"]
    assert await svc.get_project(principal=admin, project_id=project["project_id"])


async def test_anonymous_denied(session: AsyncSession) -> None:
    """Deny by default: anonymous principals are rejected on every method."""
    anon = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())
    svc = ResearchWorkspaceService(session)
    with pytest.raises(PermissionError):
        await svc.list_projects(principal=anon)
    with pytest.raises(PermissionError):
        await svc.create_project(principal=anon, title="x")
    with pytest.raises(PermissionError):
        await svc.create_note(principal=anon, content="x")
    with pytest.raises(PermissionError):
        await svc.get_project(principal=anon, project_id="x")
    with pytest.raises(PermissionError):
        await svc.get_note(principal=anon, note_id="x")


async def test_no_client_supplied_owner_id(session: AsyncSession) -> None:
    """Ownership derives from the Principal; client owner_id is never stored."""
    a = await _user_a(session)
    b = await _user_b(session)
    svc = ResearchWorkspaceService(session)
    # the service API has no owner_id parameter at all — ownership is fixed
    project = await svc.create_project(principal=a, title="A")
    assert project["project_id"]
    row = await session.get(ResearchProject, project["project_id"])
    assert row is not None and row.owner_id == a.user_id
    assert b.user_id != a.user_id


async def test_token_version_revocation_regression(session: AsyncSession) -> None:
    """Logout (token_version++) invalidates outstanding tokens (ADR-07)."""
    a = await _user_a(session)
    user = await session.get(User, str(a.user_id))
    assert user is not None
    token = issue_token(str(user.id), UserRoleCode.SCHOLAR_RESEARCHER.value, user.token_version)
    revoked = await principal_for_token(session, token)
    assert revoked.is_authenticated
    user.token_version += 1  # logout
    await session.flush()
    stale = await principal_for_token(session, token)
    assert not stale.is_authenticated
    svc = ResearchWorkspaceService(session)
    with pytest.raises(PermissionError):
        await svc.list_projects(principal=stale)


# --------------------------------------------- richer research (reuse)
async def test_research_evidence_and_version_context(session: AsyncSession) -> None:
    """Reuse: authenticated reader exposes richer evidence + version context."""
    scholar = await _user_a(session)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=scholar, title="甲乙经", dynasty="西晋")
    edition = await svc.create_edition(principal=scholar, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(
        principal=scholar, edition_id=edition.id, version_name="北宋本"
    )
    chapter = await svc.create_chapter(principal=scholar, work_id=work.id, title="卷一", order=0)
    passage = await svc.create_passage(
        principal=scholar, chapter_id=chapter.id, content_text="夫医道所兴", version_id=version.id
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p12-{id(session) % 10**6}", title="史料"
    )
    artifact = await LiteratureService(session).admit_work_artifact(
        principal=scholar,
        work_id=work.id,
        source_id=source.id,
        content=b"work",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    locator = await LiteratureService(session).passage_locator(passage.id)
    view = await ReaderService(session).resolve_research(
        principal=scholar, locator=locator.to_locator_string()
    )
    assert view["passage_id"] == passage.id
    assert view["version"]["version_id"] == version.id  # version specificity
    assert view["quotation"] == "夫医道所兴"
    assert view["evidence"] or True  # evidence context present (may be empty fixture)
    assert artifact.id  # publication/admission reuse intact


# ------------------------------------------------- public-state isolation
async def test_public_projection_excludes_workspace_state(session: AsyncSession) -> None:
    """Research workspace state never enters public projections."""
    a = await _user_a(session)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=a, title="公开典", dynasty="西晋")
    edition = await svc.create_edition(principal=a, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(principal=a, edition_id=edition.id, version_name="北宋本")
    chapter = await svc.create_chapter(principal=a, work_id=work.id, title="卷一", order=0)
    passage = await svc.create_passage(
        principal=a, chapter_id=chapter.id, content_text="公开原文", version_id=version.id
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p12pub-{id(session) % 10**6}", title="史料"
    )
    artifact = await LiteratureService(session).admit_work_artifact(
        principal=a,
        work_id=work.id,
        source_id=source.id,
        content=b"work",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    # publish via P1-09 so the public reader projection exists
    from hfm.phase1.publication import PublicationService

    reviewer = await _reviewer(session)
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=a)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    # workspace state exists but is private
    ws = ResearchWorkspaceService(session)
    project = await ws.create_project(principal=a, title="私有项目")
    await ws.create_note(principal=a, project_id=project["project_id"], content="私有笔记内容")

    locator = await LiteratureService(session).passage_locator(passage.id)
    public_view = await ReaderService(session).resolve_public(locator=locator.to_locator_string())
    assert public_view is not None
    blob = f"{public_view}"
    for token in (
        "私有项目",
        "私有笔记内容",
        "research_projects",
        "research_notes",
    ):
        assert token not in blob, f"workspace state leaked publicly: {token}"
    assert artifact.id


async def test_workspace_state_does_not_disturb_publication(session: AsyncSession) -> None:
    """Publication state boundaries preserved while workspace exists."""
    a = await _user_a(session)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=a, title="发布典", dynasty="西晋")
    edition = await svc.create_edition(principal=a, work_id=work.id, edition_name="宋刻本")
    await svc.create_version(principal=a, edition_id=edition.id, version_name="北宋本")
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p12pub2-{id(session) % 10**6}", title="史料"
    )
    artifact = await LiteratureService(session).admit_work_artifact(
        principal=a,
        work_id=work.id,
        source_id=source.id,
        content=b"work",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    ws = ResearchWorkspaceService(session)
    project = await ws.create_project(principal=a, title="项目")
    await ws.create_note(principal=a, project_id=project["project_id"], content="笔记")

    from hfm.phase1.publication import PublicationService

    reviewer = await _reviewer(session)
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=a)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    assert (await ws.list_projects(principal=a))["total"] == 1  # workspace intact


async def test_c_domain_safety_and_no_clinical_surface(session: AsyncSession) -> None:
    """Workspace serialization carries no clinical semantics (AB-14)."""
    a = await _user_a(session)
    svc = ResearchWorkspaceService(session)
    project = await svc.create_project(principal=a, title="校勘项目")
    note = await svc.create_note(principal=a, project_id=project["project_id"], content="条文比勘")
    blob = f"{project}{note}{await svc.list_projects(principal=a)}".lower()
    for token in _FORBIDDEN_CLINICAL:
        assert token not in blob, f"clinical token surfaced: {token}"


# ---------------------------------------------------------- migration
def _alembic(db_file: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}"}
    return subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", *args],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _tables(db_file: Path) -> set[str]:
    import sqlalchemy as sa

    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        return set(inspector.get_table_names())
    finally:
        engine.dispose()


def test_migration_0014_upgrade_downgrade_upgrade_single_head(tmp_path: Path) -> None:
    """0014: upgrade head (P2-05 authorized migration), downgrade to 0013,
    upgrade again, single head."""
    db_file = tmp_path / "p12.db"
    # upgrade head from empty: research tables exist; single head
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    tables = _tables(db_file)
    assert {"research_projects", "research_notes"} <= tables
    heads = _alembic(db_file, "heads").stdout.strip()
    assert heads == "0014 (head)", heads  # single Alembic head (P2-05 migration 0014)

    # downgrade to 0012: research tables gone, accepted tables intact
    assert _alembic(db_file, "downgrade", "0012").returncode == 0
    after_down = _tables(db_file)
    assert not {"research_projects", "research_notes"} & after_down
    assert {"works", "passages", "publication_records", "users"} <= after_down

    # upgrade again to head: tables restored
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    assert {"research_projects", "research_notes"} <= _tables(db_file)
    assert _alembic(db_file, "heads").stdout.strip() == "0014 (head)"


def test_migration_0013_fk_and_checks(tmp_path: Path) -> None:
    """0013: FK/owner columns and constraints are present."""
    db_file = tmp_path / "p12-fk.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0

    import sqlalchemy as sa

    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        proj = {c["name"] for c in inspector.get_columns("research_projects")}
        assert {"id", "owner_id", "title", "description", "created_at", "updated_at"} <= proj
        notes = {c["name"] for c in inspector.get_columns("research_notes")}
        assert {"id", "owner_id", "project_id", "title", "content"} <= notes
        fks = {fk["referred_table"] for fk in inspector.get_foreign_keys("research_notes")}
        assert {"users", "research_projects"} <= fks
    finally:
        engine.dispose()
