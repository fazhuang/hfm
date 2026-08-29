"""Phase 1 API v1 — auth + admin + public + research namespaces (ADR-05).

Explicit namespace separation; server-side authorization only. No internal
model serialization in public responses.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from hfm.api.v1.deps import (
    SessionDep,
    current_principal,
    require_authenticated,
    require_permission,
)
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.phase1.auth import hash_password, issue_token, verify_password
from hfm.phase1.c_domain import CDomainService
from hfm.phase1.evidence_chain import EvidenceChainService
from hfm.phase1.heritage import HeritageService
from hfm.phase1.literature import LiteratureService
from hfm.phase1.person import PersonService
from hfm.phase1.publication import PublicationService
from hfm.phase1.search import SearchService
from hfm.phase1.version_audit import AuditService, ReconciliationService, VersionLineageService
from hfm.utils.response import api_response

PrincipalDep = Annotated[Any, Depends(current_principal)]

router = APIRouter(prefix="/api/v1", tags=["phase1"])
auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
public_router = APIRouter(prefix="/api/v1/public", tags=["public"])
research_router = APIRouter(prefix="/api/v1/research", tags=["research"])


def _to_int(value: object, default: int = 0) -> int:
    """Coerce an API body value to int; malformed input fails closed."""
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return default


def _to_year(value: object) -> int | None:
    """Coerce an optional year; absent/malformed → None (fail closed)."""
    if value is None:
        return None
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------- auth
@auth_router.post("/login")
async def login(session: SessionDep, body: dict[str, str]) -> dict[str, Any]:
    """LocalDatabaseAuthProvider login → signed token (ADR-07)."""
    user = (
        await session.execute(select(User).where(User.username == body.get("username", "")))
    ).scalar_one_or_none()
    if (
        user is None
        or not verify_password(body.get("password", ""), user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(status_code=401, detail="invalid credentials")
    role = (
        (
            await session.execute(
                select(Role.code)
                .join(user_roles, user_roles.c.role_id == Role.id)
                .where(user_roles.c.user_id == user.id)
            )
        )
        .scalars()
        .first()
    )
    token = issue_token(
        user.id, str(role or UserRoleCode.ANONYMOUS_VISITOR.value), user.token_version
    )
    return api_response(data={"ok": True, "token": token, "user_id": user.id, "role": role})


@auth_router.post("/logout", dependencies=[Depends(require_authenticated)])
async def logout(session: SessionDep, principal: PrincipalDep) -> dict[str, Any]:
    """Invalidate outstanding tokens immediately (ADR-07 Guard-03)."""
    user = await session.get(User, str(principal.user_id))
    if user is not None:
        user.token_version += 1
        await session.flush()
    return api_response(data={"ok": True})


@admin_router.post("/users", dependencies=[Depends(require_permission("user:manage"))])
async def create_user(session: SessionDep, body: dict[str, str]) -> dict[str, Any]:
    """SYSTEM_ADMIN creates an HFM-native user (no HFB credential migration)."""
    role_code = body.get("role", UserRoleCode.STUDENT_RESEARCHER.value)
    if role_code not in {r.value for r in UserRoleCode}:
        raise HTTPException(status_code=400, detail="unknown role")
    user = User(
        username=body.get("username", ""), password_hash=hash_password(body.get("password", ""))
    )
    session.add(user)
    await session.flush()
    role = (await session.execute(select(Role).where(Role.code == role_code))).scalar_one_or_none()
    if role is not None:
        await session.execute(user_roles.insert().values(user_id=user.id, role_id=role.id))
        await session.flush()
    return api_response(data={"ok": True, "user_id": user.id, "role": role_code})


@admin_router.post(
    "/users/{user_id}/roles", dependencies=[Depends(require_permission("user:manage"))]
)
async def assign_role(session: SessionDep, user_id: str, body: dict[str, str]) -> dict[str, Any]:
    """SYSTEM_ADMIN assigns a frozen role (unauthorized assignment rejected)."""
    role_code = body.get("role", "")
    if role_code not in {r.value for r in UserRoleCode}:
        raise HTTPException(status_code=400, detail="unknown role")
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    role = (await session.execute(select(Role).where(Role.code == role_code))).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role.id))
    await session.flush()
    return api_response(data={"ok": True, "user_id": user.id, "role": role_code})


# ---------------------------------------------------------------- public
@public_router.get("/search")
async def public_search(
    session: SessionDep, q: str = "", page: int = 1, page_size: int = 20
) -> dict[str, Any]:
    """Anonymous public search — PUBLISHED projection only (ADR-02/05)."""
    result = await SearchService(session).public_search(query=q, page=page, page_size=page_size)
    return api_response(
        data={
            "hits": [
                {
                    "kind": h.kind,
                    "id": h.id,
                    "title": h.title,
                    "snippet": h.snippet,
                    "version_id": h.version_id,
                    "publication_status": h.publication_status,
                }
                for h in result.hits
            ],
            "total": result.total,
            "page": result.page,
        }
    )


@public_router.get("/persons/{entity_id}")
async def public_person(session: SessionDep, entity_id: str) -> dict[str, Any]:
    """P1-03: public person projection — PUBLISHED only (404 otherwise)."""
    record = await PersonService(session).get_public_person(entity_id)
    if record is None:
        raise HTTPException(status_code=404, detail="person not published")
    return api_response(data=record)


@public_router.get("/works/{work_id}")
async def public_work(session: SessionDep, work_id: str) -> dict[str, Any]:
    """P1-04: public work projection — PUBLISHED lineage only (404 otherwise)."""
    record = await LiteratureService(session).get_public_work(work_id)
    if record is None:
        raise HTTPException(status_code=404, detail="work not published")
    return api_response(data=record)


@public_router.get("/c-terms/{entity_id}")
async def public_c_term(session: SessionDep, entity_id: str) -> dict[str, Any]:
    """P1-05: public C-domain term — PUBLISHED, evidenced relations only.

    Returns the historical term + related structured historical records +
    original text/source (canonical passage) with version context. No
    clinical recommendation surface (AB-14).
    """
    record = await CDomainService(session).get_public_term(entity_id)
    if record is None:
        raise HTTPException(status_code=404, detail="c-domain term not published")
    return api_response(data=record)


@public_router.get("/heritage/{entity_id}")
async def public_heritage(session: SessionDep, entity_id: str) -> dict[str, Any]:
    """P1-06: public heritage project — PUBLISHED, evidenced lineage only."""
    record = await HeritageService(session).get_public_project(entity_id)
    if record is None:
        raise HTTPException(status_code=404, detail="heritage project not published")
    return api_response(data=record)


# ---------------------------------------------------------------- research
@research_router.get("/search", dependencies=[Depends(require_authenticated)])
async def research_search(
    session: SessionDep, principal: PrincipalDep, q: str = ""
) -> dict[str, Any]:
    result = await SearchService(session).research_search(query=q, principal=principal)
    return api_response(
        data={
            "hits": [{"kind": h.kind, "id": h.id, "title": h.title} for h in result.hits],
            "total": result.total,
        }
    )


@research_router.get("/evidence-chain/{citation_id}", dependencies=[Depends(require_authenticated)])
async def evidence_chain(session: SessionDep, citation_id: str) -> dict[str, Any]:
    """P1-02: fail-closed chain resolution (Source→SourceRef→Evidence→Citation)."""
    chain = await EvidenceChainService(session).resolve_citation(citation_id)
    return api_response(
        data={
            "citation_id": chain.citation_id,
            "assertion_id": chain.assertion_id,
            "evidence_ids": list(chain.evidence_ids),
            "source_ref_ids": list(chain.source_ref_ids),
            "source_ids": list(chain.source_ids),
        }
    )


# ------------------------------------------------- P1-03 A-domain (research)
@research_router.post("/persons", dependencies=[Depends(require_authenticated)])
async def research_create_person(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    """Create a canonical person record (assertion:create; no publication)."""
    person = await PersonService(session).create_person(
        principal=principal,
        name_zh=body.get("name_zh"),
        name_pinyin=body.get("name_pinyin"),
        courtesy_name=body.get("courtesy_name"),
        pseudonym=body.get("pseudonym"),
        dynasty=body.get("dynasty"),
    )
    return api_response(data={"entity_id": person.entity_id})


@research_router.post(
    "/persons/{entity_id}/assertions", dependencies=[Depends(require_authenticated)]
)
async def research_add_assertion(
    session: SessionDep, principal: PrincipalDep, entity_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Add an evidenced biographical assertion about the person."""
    assertion = await PersonService(session).add_biographical_assertion(
        principal=principal,
        person_entity_id=entity_id,
        predicate=str(body.get("predicate", "")),
        value=body.get("value"),
        object_entity_id=body.get("object_entity_id"),
        evidence_ids=tuple(str(e) for e in (body.get("evidence_ids") or [])),
        confidence=str(body.get("confidence", "medium")),
        assertion_type=str(body.get("assertion_type", "biographical")),
    )
    return api_response(data={"id": assertion.id, "subject_entity_id": assertion.subject_entity_id})


@research_router.post("/persons/{entity_id}/events", dependencies=[Depends(require_authenticated)])
async def research_add_event(
    session: SessionDep, principal: PrincipalDep, entity_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Create a 生平事件 for the person (CD-6 Event + relation)."""
    event = await PersonService(session).create_event(
        principal=principal,
        person_entity_id=entity_id,
        event_type=str(body.get("event_type", "other")),
        start_year=body.get("start_year"),
        start_month=body.get("start_month"),
        start_day=body.get("start_day"),
        start_precision=str(body.get("start_precision", "unknown")),
        start_approximate=bool(body.get("start_approximate", False)),
        end_year=body.get("end_year"),
        end_month=body.get("end_month"),
        end_day=body.get("end_day"),
        end_precision=str(body.get("end_precision", "unknown")),
        end_approximate=bool(body.get("end_approximate", False)),
        role=str(body.get("role", "actor")),
    )
    return api_response(data={"event_id": event.entity_id})


@research_router.get("/persons/{entity_id}", dependencies=[Depends(require_authenticated)])
async def research_get_person(
    session: SessionDep, principal: PrincipalDep, entity_id: str
) -> dict[str, Any]:
    """Research person record: evidence + publication state (auth required)."""
    return api_response(data=await PersonService(session).get_research_person(entity_id))


# ------------------------------------------------- P1-04 B-domain (research)
@research_router.post("/works", dependencies=[Depends(require_authenticated)])
async def research_create_work(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    """Create a canonical Work (typed-Entity identity; no publication)."""
    work = await LiteratureService(session).create_work(
        principal=principal,
        title=str(body.get("title", "")),
        author_entity_id=body.get("author_entity_id"),
        dynasty=body.get("dynasty"),
        category=body.get("category"),
        description=body.get("description"),
        is_extant=bool(body.get("is_extant", True)),
    )
    return api_response(data={"work_id": work.id, "entity_id": work.entity_id})


@research_router.post("/works/{work_id}/editions", dependencies=[Depends(require_authenticated)])
async def research_create_edition(
    session: SessionDep, principal: PrincipalDep, work_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    edition = await LiteratureService(session).create_edition(
        principal=principal,
        work_id=work_id,
        edition_name=str(body.get("edition_name", "")),
        era=body.get("era"),
        publisher_block=body.get("publisher_block"),
        preface_postscript=body.get("preface_postscript"),
        lineage_parent_edition_id=body.get("lineage_parent_edition_id"),
    )
    return api_response(data={"edition_id": edition.id})


@research_router.post(
    "/works/{work_id}/editions/{edition_id}/versions",
    dependencies=[Depends(require_authenticated)],
)
async def research_create_version(
    session: SessionDep,
    principal: PrincipalDep,
    work_id: str,
    edition_id: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    edition = await LiteratureService(session).create_version(
        principal=principal,
        edition_id=edition_id,
        version_name=str(body.get("version_name", "")),
        era=body.get("era"),
        year=body.get("year"),
        repository=body.get("repository"),
        shelf_mark=body.get("shelf_mark"),
        editor=body.get("editor"),
        description=body.get("description"),
        is_formal_source=bool(body.get("is_formal_source", False)),
        parent_version_id=body.get("parent_version_id"),
    )
    return api_response(data={"version_id": edition.id})


@research_router.post("/works/{work_id}/chapters", dependencies=[Depends(require_authenticated)])
async def research_create_chapter(
    session: SessionDep, principal: PrincipalDep, work_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    chapter = await LiteratureService(session).create_chapter(
        principal=principal,
        work_id=work_id,
        title=str(body.get("title", "")),
        order=_to_int(body.get("order", 0)),
        parent_id=body.get("parent_id"),
    )
    return api_response(data={"chapter_id": chapter.id})


@research_router.post(
    "/chapters/{chapter_id}/passages", dependencies=[Depends(require_authenticated)]
)
async def research_create_passage(
    session: SessionDep, principal: PrincipalDep, chapter_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    passage = await LiteratureService(session).create_passage(
        principal=principal,
        chapter_id=chapter_id,
        content_text=str(body.get("content_text", "")),
        order=_to_int(body.get("order", 0)),
        version_id=body.get("version_id"),
        translation=body.get("translation"),
        notes=body.get("notes"),
        tags=body.get("tags"),
    )
    locator = await LiteratureService(session).passage_locator(passage.id)
    return api_response(data={"passage_id": passage.id, "locator": locator.to_locator_string()})


@research_router.get("/works/{work_id}", dependencies=[Depends(require_authenticated)])
async def research_get_work(
    session: SessionDep, principal: PrincipalDep, work_id: str
) -> dict[str, Any]:
    """Research work record: lineage + rights + publication state."""
    return api_response(data=await LiteratureService(session).get_research_work(work_id))


# ------------------------------------------- P1-05 C-domain (research)
@research_router.post("/c-terms", dependencies=[Depends(require_authenticated)])
async def research_create_c_term(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    """Create a canonical C-domain term (assertion:create; no publication)."""
    term = await CDomainService(session).create_term(
        principal=principal,
        term_type=str(body.get("term_type", "")),
        term_name=str(body.get("term_name", "")),
        canonical_passage_id=body.get("canonical_passage_id"),
        description=body.get("description"),
    )
    return api_response(data={"entity_id": term.entity_id})


@research_router.post(
    "/c-terms/{entity_id}/relations", dependencies=[Depends(require_authenticated)]
)
async def research_create_c_relation(
    session: SessionDep, principal: PrincipalDep, entity_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Create a structured historical relation between two C terms."""
    relation = await CDomainService(session).create_relation(
        principal=principal,
        source_term_entity_id=entity_id,
        target_term_entity_id=str(body.get("target_term_entity_id", "")),
        relation_type=str(body.get("relation_type", "")),
        evidence_id=body.get("evidence_id"),
        description=body.get("description"),
    )
    return api_response(data={"relation_id": relation.id, "relation_type": relation.relation_type})


@research_router.get("/c-terms/{entity_id}", dependencies=[Depends(require_authenticated)])
async def research_get_c_term(
    session: SessionDep, principal: PrincipalDep, entity_id: str
) -> dict[str, Any]:
    """Research C-domain term record: relations + source/version context."""
    return api_response(data=await CDomainService(session).get_research_term(entity_id))


# ------------------------------------------- P1-06 D-domain (research)
@research_router.post("/heritage", dependencies=[Depends(require_authenticated)])
async def research_create_heritage_project(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    """Create a canonical heritage project (assertion:create; no publication)."""
    project = await HeritageService(session).create_project(
        principal=principal,
        project_name=str(body.get("project_name", "")),
        official_name=body.get("official_name"),
        category=body.get("category"),
        description=body.get("description"),
    )
    return api_response(data={"entity_id": project.entity_id})


@research_router.post(
    "/heritage/{entity_id}/relations", dependencies=[Depends(require_authenticated)]
)
async def research_create_heritage_relation(
    session: SessionDep, principal: PrincipalDep, entity_id: str, body: dict[str, Any]
) -> dict[str, Any]:
    """Create an evidenced lineage relation (official-name carried)."""
    relation = await HeritageService(session).create_relation(
        principal=principal,
        project_entity_id=entity_id,
        subject_entity_id=str(body.get("subject_entity_id", "")),
        relation_role=str(body.get("relation_role", "")),
        official_name=body.get("official_name"),
        start_year=_to_year(body.get("start_year")),
        end_year=_to_year(body.get("end_year")),
        evidence_id=body.get("evidence_id"),
        description=body.get("description"),
    )
    return api_response(data={"relation_id": relation.id, "relation_role": relation.relation_role})


@research_router.get("/heritage/{entity_id}", dependencies=[Depends(require_authenticated)])
async def research_get_heritage_project(
    session: SessionDep, principal: PrincipalDep, entity_id: str
) -> dict[str, Any]:
    """Research heritage project record: lineage + official-name + state."""
    return api_response(data=await HeritageService(session).get_research_project(entity_id))


@research_router.post("/artifacts", dependencies=[Depends(require_authenticated)])
async def research_submit_artifact(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    """Admission (P1-01) with domain-entity binding for A/B records."""
    from hfm.models.content_artifact import ProvenanceStatus, RightsStatus

    subject_kind = str(body.get("subject_kind", "person"))
    subject_id = str(body.get("subject_id", ""))
    content = str(body.get("content", "")).encode("utf-8")
    source_id = str(body.get("source_id", ""))
    rights = RightsStatus(str(body.get("rights_status", "unknown")))
    provenance = ProvenanceStatus(str(body.get("provenance_status", "pending")))
    if subject_kind == "person":
        artifact = await PersonService(session).admit_person_artifact(
            principal=principal,
            person_entity_id=subject_id,
            source_id=source_id,
            content=content,
            rights_status=rights,
            provenance_status=provenance,
            format=body.get("format"),
            version_id=body.get("version_id"),
        )
    elif subject_kind == "work":
        artifact = await LiteratureService(session).admit_work_artifact(
            principal=principal,
            work_id=subject_id,
            source_id=source_id,
            content=content,
            rights_status=rights,
            provenance_status=provenance,
            format=body.get("format"),
            version_id=body.get("version_id"),
        )
    elif subject_kind == "c_term":
        artifact = await CDomainService(session).admit_term_artifact(
            principal=principal,
            term_entity_id=subject_id,
            source_id=source_id,
            content=content,
            rights_status=rights,
            provenance_status=provenance,
            format=body.get("format"),
            version_id=body.get("version_id"),
        )
    elif subject_kind == "heritage":
        artifact = await HeritageService(session).admit_project_artifact(
            principal=principal,
            project_entity_id=subject_id,
            source_id=source_id,
            content=content,
            rights_status=rights,
            provenance_status=provenance,
            format=body.get("format"),
            version_id=body.get("version_id"),
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="subject_kind must be person, work, c_term or heritage",
        )
    return api_response(
        data={
            "artifact_id": artifact.id,
            "admission_state": artifact.admission_state,
            "rejection_reason": artifact.rejection_reason,
        }
    )


@research_router.post(
    "/artifacts/{artifact_id}/submit", dependencies=[Depends(require_authenticated)]
)
async def research_submit_for_review(
    session: SessionDep, principal: PrincipalDep, artifact_id: str
) -> dict[str, Any]:
    """Creator submits an ADMITTED artifact for publication review (P1-09)."""
    record = await PublicationService(session).submit_for_review(
        artifact_id=artifact_id, creator=principal
    )
    return api_response(
        data={"artifact_id": record.artifact_id, "status": record.publication_status}
    )


# ---------------------------------------------------------------- admin
@admin_router.post(
    "/publication/review", dependencies=[Depends(require_permission("content:review"))]
)
async def publication_review(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    record = await PublicationService(session).review(
        artifact_id=str(body.get("artifact_id", "")),
        reviewer=principal,
        approve=bool(body.get("approve", False)),
    )
    return api_response(
        data={"artifact_id": record.artifact_id, "status": record.publication_status}
    )


@admin_router.post(
    "/publication/publish", dependencies=[Depends(require_permission("content:publish"))]
)
async def publication_publish(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    record = await PublicationService(session).publish(
        artifact_id=str(body.get("artifact_id", "")), actor=principal
    )
    return api_response(
        data={"artifact_id": record.artifact_id, "status": record.publication_status}
    )


@admin_router.post(
    "/publication/withdraw", dependencies=[Depends(require_permission("content:withdraw"))]
)
async def publication_withdraw(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    record = await PublicationService(session).withdraw(
        artifact_id=str(body.get("artifact_id", "")), actor=principal
    )
    return api_response(
        data={"artifact_id": record.artifact_id, "status": record.publication_status}
    )


@admin_router.get("/search", dependencies=[Depends(require_permission("content:review"))])
async def admin_search(session: SessionDep, principal: PrincipalDep, q: str = "") -> dict[str, Any]:
    result = await SearchService(session).admin_search(query=q, principal=principal)
    return api_response(data={"total": result.total, "hits": [h.id for h in result.hits]})


# ------------------------------------------------- P1-13 audit/reconciliation
@admin_router.post("/reconciliation", dependencies=[Depends(require_permission("content:review"))])
async def admin_reconciliation(
    session: SessionDep, principal: PrincipalDep, body: dict[str, Any]
) -> dict[str, Any]:
    """Run a governed reconciliation (E-13); mismatch fails closed (recorded FAIL)."""
    run = await ReconciliationService(session).reconcile(
        scope=str(body.get("scope", "")),
        expected_count=_to_int(body.get("expected_count", 0)),
        expected_hash=str(body.get("expected_hash", "")),
        created_by=principal.user_id,
    )
    return api_response(
        data={
            "run_id": run.id,
            "scope": run.scope,
            "expected_count": run.expected_count,
            "actual_count": run.actual_count,
            "status": run.status,
        }
    )


@admin_router.get("/audit-log", dependencies=[Depends(require_permission("audit:read"))])
async def admin_audit_log(session: SessionDep, limit: int = 50) -> dict[str, Any]:
    """Append-only governed-state journal (P1-13 auditability)."""
    entries = await AuditService(session).list_recent(limit=limit)
    return api_response(
        data=[
            {
                "id": e.id,
                "actor_id": e.actor_id,
                "action": e.action,
                "target_type": e.target_type,
                "target_id": e.target_id,
                "detail": e.detail,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ]
    )


@admin_router.get("/lineage/{version_id}", dependencies=[Depends(require_permission("audit:read"))])
async def admin_lineage(session: SessionDep, version_id: str) -> dict[str, Any]:
    """Deterministic version lineage + digest (P1-13; fail-closed on breakage)."""
    service = VersionLineageService(session)
    chain = await service.lineage(version_id)
    return api_response(
        data={
            "version_id": version_id,
            "lineage_hash": await service.lineage_hash(version_id),
            "chain": [
                {
                    "version_id": node.version_id,
                    "version_name": node.version_name,
                    "edition_id": node.edition_id,
                    "parent_version_id": node.parent_version_id,
                }
                for node in chain
            ],
        }
    )
