"""Phase 1 API dependencies (ADR-05 / ADR-07 — server-side enforcement)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.db.session import get_session
from hfm.phase1.auth import Principal, principal_for_token

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def current_principal(
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Principal:
    """Resolve the Bearer token to a Principal (anonymous when absent/invalid)."""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    return await principal_for_token(session, token)


async def require_authenticated(
    principal: Annotated[Principal, Depends(current_principal)],
) -> Principal:
    """Authentication-required boundary: anonymous callers are rejected 401.

    WR00-B2 authfix: the boundary previously leaked a raw PermissionError that
    the catch-all mapped to HTTP 500; authentication-required routes now fail
    closed with the documented 401 so clients can revoke/redirect (P2-02-AC-04).
    Authorization semantics are unchanged (deny-by-default).
    """
    if not principal.is_authenticated:
        raise HTTPException(status_code=401, detail="authentication required")
    return principal


def require_permission(code: str) -> Any:
    """Permission-required boundary (default deny): missing permission → 403.

    WR00-B2 authfix: same status-code repair as require_authenticated; the
    permission matrix and deny logic are untouched.
    """

    async def _dep(principal: Annotated[Principal, Depends(current_principal)]) -> Principal:
        if not principal.is_authenticated or not principal.has_permission(code):
            raise HTTPException(status_code=403, detail=f"missing permission: {code}")
        return principal

    return _dep
