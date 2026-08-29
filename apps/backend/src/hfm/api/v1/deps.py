"""Phase 1 API dependencies (ADR-05 / ADR-07 — server-side enforcement)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Header
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
    """Research boundary: authentication required (401 semantics — raise)."""
    if not principal.is_authenticated:
        raise PermissionError("authentication required")
    return principal


def require_permission(code: str) -> Any:
    """Admin boundary: permission required (default deny)."""

    async def _dep(principal: Annotated[Principal, Depends(current_principal)]) -> Principal:
        if not principal.is_authenticated or not principal.has_permission(code):
            raise PermissionError(f"missing permission: {code}")
        return principal

    return _dep
