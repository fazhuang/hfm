"""API permission-status regression (minimum boundary fix).

Proves apps/backend/src/hfm/api/v1/deps.py maps auth/authorization edges to
correct HTTP status codes (not 500):
  - require_authenticated: anonymous -> 401
  - require_permission: authenticated-without-code -> 403
  - authorized (has permission) -> 200
  - error envelope preserved (success: false) and X-Request-ID retained.
Deny-by-default and the permission set are unchanged (unit-level RBAC tests in
test_phase1_rbac.py cover the matrix); this file proves the HTTP boundary.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from hfm.api.v1.deps import current_principal, require_authenticated, require_permission
from hfm.core.error_handlers import register_error_handlers
from hfm.middleware.request_id import RequestIDMiddleware
from hfm.phase1.auth import Principal

app = FastAPI()
app.add_middleware(RequestIDMiddleware)
register_error_handlers(app)


def _principal(
    user_id: str | None,
    roles: tuple[str, ...],
    permissions: frozenset[str],
) -> Principal:
    return Principal(user_id=user_id, roles=roles, permissions=permissions)


async def override_anonymous() -> Principal:
    return _principal(None, ("ANONYMOUS_VISITOR",), frozenset())


async def override_researcher() -> Principal:
    return _principal("u1", ("STUDENT_RESEARCHER",), frozenset())


async def override_reviewer() -> Principal:
    return _principal("u2", ("CONTENT_REVIEWER",), frozenset({"content:review"}))


@app.get("/probe/authenticated")
async def probe_auth(
    _: Annotated[Principal, Depends(require_authenticated)],
) -> dict[str, object]:
    return {"ok": True}


@app.get("/probe/permission")
async def probe_perm(
    _: Annotated[Principal, Depends(require_permission("content:review"))],
) -> dict[str, object]:
    return {"ok": True}


def _client(override: Callable[[], Awaitable[Principal]]) -> TestClient:
    app.dependency_overrides[current_principal] = override
    return TestClient(app)


def test_anonymous_protected_route_returns_401() -> None:
    client = _client(override_anonymous)
    resp = client.get("/probe/authenticated")
    assert resp.status_code == 401
    body = resp.json()
    assert body.get("success") is False
    assert resp.headers.get("x-request-id")  # X-Request-ID preserved


def test_authenticated_missing_permission_returns_403() -> None:
    client = _client(override_researcher)  # has no content:review
    resp = client.get("/probe/permission")
    assert resp.status_code == 403
    assert resp.json().get("success") is False
    assert resp.headers.get("x-request-id")


def test_authorized_role_returns_200() -> None:
    client = _client(override_reviewer)  # has content:review
    resp = client.get("/probe/permission")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_403_zero_500_no_500() -> None:
    # Regression guard: a missing permission must never surface as 500.
    client = _client(override_researcher)
    resp = client.get("/probe/permission")
    assert resp.status_code != 500
