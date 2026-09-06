# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
# The canonical gates (`mypy src tests`) resolve hfm to source and pass;
# per-file mypy/pyright see the editable install and flag import-untyped /
# reportMissingImports on the existing hfm imports. File-level suppression
# keeps the per-file guard green without weakening the real gate.
"""ND-1 B05 — authoritative auth login API contract (mounted-route evidence).

Proves the frozen backend contract that the frontend adapter consumes:
`POST /api/v1/auth/login` (mounted FastAPI route) returns the shared
`api_response` envelope `{success,timestamp,message,data:{ok,token,user_id,
role}}` for an active seeded user; invalid credentials are rejected with
HTTP 401 and never return a token; the issued bearer token resolves to the
same identity/role server-side (default deny preserved).

No backend API/controller/auth-engine code is modified by B05 — this file
only records the existing wire contract for the frontend repair.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import hfm.models.content_artifact  # noqa: F401

# Register every model so Base.metadata is complete for the mounted app
# (same import surface as tests/conftest.py).
import hfm.models.identity  # noqa: F401
import hfm.models.passage  # noqa: F401
import hfm.models.research_workspace  # noqa: F401
import hfm.models.work  # noqa: F401
from hfm.db.base import Base
from hfm.db.session import get_session
from hfm.main import app
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.phase1.auth import ensure_roles_seeded, hash_password, principal_for_token

USERNAME = "contract-researcher"
PASSWORD = "correct-horse-battery"


@pytest_asyncio.fixture
async def seeded_app() -> AsyncIterator[tuple[AsyncEngine, str]]:
    """Isolated SQLite app with one active STUDENT_RESEARCHER user."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with factory() as session:
        await ensure_roles_seeded(session)
        user = User(username=USERNAME, password_hash=hash_password(PASSWORD))
        session.add(user)
        await session.flush()
        role_row = (
            await session.execute(
                select(Role).where(Role.code == UserRoleCode.STUDENT_RESEARCHER.value)
            )
        ).scalar_one()
        await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
        await session.commit()
        user_id = user.id

    async def _override() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = _override
    try:
        yield engine, str(user_id)
    finally:
        app.dependency_overrides.pop(get_session, None)
        await engine.dispose()


async def _client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def _login(client: httpx.AsyncClient, username: str, password: str) -> httpx.Response:
    return await client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )


async def test_login_success_envelope_shape(
    seeded_app: tuple[AsyncEngine, str], client: httpx.AsyncClient
) -> None:
    """Seeded active user → mounted login returns the authoritative envelope."""
    _, user_id = seeded_app
    response = await _login(client, USERNAME, PASSWORD)
    assert response.status_code == 200
    body = response.json()
    # Authoritative api_response envelope shape (B05_BACKEND_ACTUAL_RESPONSE).
    assert body["success"] is True
    assert isinstance(body.get("message"), str)
    assert isinstance(body.get("timestamp"), str)
    data = body["data"]
    assert data["ok"] is True
    assert isinstance(data["token"], str) and len(data["token"]) > 0
    assert data["user_id"] == user_id
    assert data["role"] == UserRoleCode.STUDENT_RESEARCHER.value
    # No top-level token/user fields exist on the wire (frontend must adapt).
    assert "token" not in body or body["token"] is None
    assert "user" not in body


async def test_login_invalid_credentials_rejected_401(
    seeded_app: tuple[AsyncEngine, str], client: httpx.AsyncClient
) -> None:
    """Wrong password / unknown user → HTTP 401, never a token (fail closed)."""
    for username, password in ((USERNAME, "wrong-password"), ("ghost", "x")):
        response = await _login(client, username, password)
        assert response.status_code == 401
        error_body = response.json()
        assert error_body["success"] is False
        assert error_body["data"] is None
        assert "token" not in error_body


async def test_login_token_resolves_to_same_identity(
    seeded_app: tuple[AsyncEngine, str], client: httpx.AsyncClient
) -> None:
    """The issued token resolves server-side to the same user/role (default deny)."""
    engine, user_id = seeded_app
    response = await _login(client, USERNAME, PASSWORD)
    token = response.json()["data"]["token"]

    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        principal = await principal_for_token(session, token)
        assert principal.is_authenticated
        assert principal.user_id == user_id
        assert UserRoleCode.STUDENT_RESEARCHER.value in principal.roles
        # Researcher may create personal research notes (research surface)…
        assert principal.has_permission("research:note:create")
        # …but never admin actions (content:publish stays denied for students).
        assert not principal.has_permission("content:publish")
        assert not principal.has_permission("user:manage")


async def test_research_allowed_and_admin_denied_for_student(
    seeded_app: tuple[AsyncEngine, str], client: httpx.AsyncClient
) -> None:
    """Mounted routes: student token passes research auth; admin stays denied."""
    response = await _login(client, USERNAME, PASSWORD)
    headers = {"Authorization": f"Bearer {response.json()['data']['token']}"}

    research = await client.get("/api/v1/research/search", headers=headers)
    assert research.status_code == 200
    assert research.json()["success"] is True

    admin = await client.get("/api/v1/admin/audit-log", headers=headers)
    assert admin.status_code != 200
    assert admin.json()["success"] is False


async def test_anonymous_protected_access_is_denied(
    seeded_app: tuple[AsyncEngine, str], client: httpx.AsyncClient
) -> None:
    """No bearer token → protected research/admin access is never granted."""
    research = await client.get("/api/v1/research/search")
    assert research.status_code != 200
    assert research.json()["success"] is False
    admin = await client.get("/api/v1/admin/audit-log")
    assert admin.status_code != 200
    assert admin.json()["success"] is False


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
