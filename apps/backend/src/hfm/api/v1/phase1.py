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
from hfm.phase1.evidence_chain import EvidenceChainService
from hfm.phase1.publication import PublicationService
from hfm.phase1.search import SearchService
from hfm.utils.response import api_response

PrincipalDep = Annotated[Any, Depends(current_principal)]

router = APIRouter(prefix="/api/v1", tags=["phase1"])
auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
public_router = APIRouter(prefix="/api/v1/public", tags=["public"])
research_router = APIRouter(prefix="/api/v1/research", tags=["research"])


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
