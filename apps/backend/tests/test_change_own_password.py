# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
# The canonical gates (`mypy src tests`) resolve hfm to source and pass;
# per-file mypy/pyright see the editable install and flag import-untyped /
# reportMissingImports on the existing hfm imports. File-level suppression
# keeps the per-file guard green without weakening the real gate.
"""WR00-B2 — change-own-password contract (mounted-route evidence).

Proves the self-service password-change endpoint (`POST
/api/v1/auth/change-password`) against the mounted application on an isolated
database:

  - unauthenticated / wrong-current / policy-invalid new password → REJECT
    and the stored hash is never modified;
  - a valid change → PASS; the OLD password then FAILS authentication and the
    NEW password authenticates (login + token), and the pre-change token is
    revoked (ADR-07 Guard-03);
  - it is impossible to change ANOTHER user's password through the interface
    (the target is always the authenticated principal; a body-supplied
    user id is ignored and another user's credentials stay valid even when
    their current password is known);
  - password storage stays a salted scrypt hash — plaintext is never stored.

Existing auth/RBAC hashing and token logic is reused (`hash_password` /
`verify_password` / token_version revocation); no new credential scheme is
introduced.
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
import hfm.models.identity  # noqa: F401
import hfm.models.passage  # noqa: F401
import hfm.models.research_workspace  # noqa: F401
import hfm.models.work  # noqa: F401
from hfm.db.base import Base
from hfm.db.session import get_session
from hfm.main import app
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.phase1.auth import ensure_roles_seeded, hash_password, verify_password

ALICE_USERNAME = "alice-researcher"
ALICE_PW = "A-current-password-2026!"
BOB_USERNAME = "bob-reviewer"
BOB_PW = "B-current-password-2026!"


async def _seed_user(
    session: AsyncSession, username: str, password: str, role_code: UserRoleCode
) -> str:
    await ensure_roles_seeded(session)
    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    await session.flush()
    role_row = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
    await session.flush()
    return str(user.id)


@pytest_asyncio.fixture
async def seeded_app() -> AsyncIterator[tuple[AsyncEngine, dict[str, str]]]:
    """Isolated SQLite app: alice (STUDENT_RESEARCHER) + bob (CONTENT_REVIEWER).

    The get_session override mirrors hfm.db.session.get_session semantics
    (commit on success / rollback on error) so route writes persist for
    read-back assertions — unlike the read-only contract fixture.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with factory() as session:
        alice_id = await _seed_user(
            session, ALICE_USERNAME, ALICE_PW, UserRoleCode.STUDENT_RESEARCHER
        )
        bob_id = await _seed_user(session, BOB_USERNAME, BOB_PW, UserRoleCode.CONTENT_REVIEWER)
        await session.commit()

    async def _override() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except BaseException:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = _override
    try:
        yield engine, {"alice": alice_id, "bob": bob_id}
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


async def _token(client: httpx.AsyncClient, username: str, password: str) -> str:
    response = await _login(client, username, password)
    assert response.status_code == 200, response.text
    return str(response.json()["data"]["token"])


async def _change(
    client: httpx.AsyncClient, token: str, current: str, new: str, **extra: str
) -> httpx.Response:
    body: dict[str, str] = {
        "current_password": current,
        "new_password": new,
        **extra,
    }
    return await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
    )


async def _stored_hash(engine: AsyncEngine, username: str) -> tuple[str | None, int | None]:
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        user = (
            await session.execute(select(User).where(User.username == username))
        ).scalar_one_or_none()
        if user is None:
            return None, None
        return str(user.password_hash), user.token_version


async def test_change_password_unauthenticated_rejected(
    seeded_app: tuple[AsyncEngine, dict[str, str]], client: httpx.AsyncClient
) -> None:
    """No bearer token → 401; the stored credential is untouched."""
    _, _ = seeded_app
    before_hash, before_version = await _stored_hash(seeded_app[0], ALICE_USERNAME)
    response = await _change(client, "", ALICE_PW, "A-brand-new-password-2026!")
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    after_hash, after_version = await _stored_hash(seeded_app[0], ALICE_USERNAME)
    assert after_hash == before_hash
    assert after_version == before_version


async def test_change_password_wrong_current_rejected(
    seeded_app: tuple[AsyncEngine, dict[str, str]], client: httpx.AsyncClient
) -> None:
    """Authenticated but wrong current password → REJECT; hash unchanged."""
    alice_id = seeded_app[1]["alice"]
    token = await _token(client, ALICE_USERNAME, ALICE_PW)
    assert token
    before_hash, before_version = await _stored_hash(seeded_app[0], ALICE_USERNAME)
    response = await _change(client, token, "totally-wrong-current", "A-brand-new-password-2026!")
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "current password" in body["message"]
    after_hash, after_version = await _stored_hash(seeded_app[0], ALICE_USERNAME)
    assert after_hash == before_hash
    assert after_version == before_version
    # The existing credential still authenticates (nothing changed).
    assert alice_id == (await _login(client, ALICE_USERNAME, ALICE_PW)).json()["data"]["user_id"]


async def test_change_password_invalid_new_rejected(
    seeded_app: tuple[AsyncEngine, dict[str, str]], client: httpx.AsyncClient
) -> None:
    """Policy-invalid new passwords (short / default / contains username) → 400."""
    alice_id = seeded_app[1]["alice"]
    token = await _token(client, ALICE_USERNAME, ALICE_PW)
    assert token
    before_hash, before_version = await _stored_hash(seeded_app[0], ALICE_USERNAME)
    for bad_new in ("short", "admin123", "A-current-password-2026!", ALICE_USERNAME + "-x"):
        response = await _change(client, token, ALICE_PW, bad_new)
        assert response.status_code == 400, bad_new
        assert response.json()["success"] is False
    after_hash, after_version = await _stored_hash(seeded_app[0], ALICE_USERNAME)
    assert after_hash == before_hash
    assert after_version == before_version
    assert alice_id == (await _login(client, ALICE_USERNAME, ALICE_PW)).json()["data"]["user_id"]


async def test_change_password_missing_fields_rejected(
    seeded_app: tuple[AsyncEngine, dict[str, str]], client: httpx.AsyncClient
) -> None:
    """Missing current or new password → REJECT (fields are required)."""
    token = await _token(client, ALICE_USERNAME, ALICE_PW)
    assert token
    response = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert response.status_code == 400
    assert response.json()["success"] is False


async def test_change_password_valid_success(
    seeded_app: tuple[AsyncEngine, dict[str, str]], client: httpx.AsyncClient
) -> None:
    """Valid change → PASS; old password FAILS, new password authenticates.

    Proves OLD_PASSWORD_AUTHENTICATION=FAIL and
    NEW_PASSWORD_AUTHENTICATION=PASS after a successful self-service change.
    """
    alice_id = seeded_app[1]["alice"]
    old_token = await _token(client, ALICE_USERNAME, ALICE_PW)
    new_pw = "A-brand-new-password-2026!"

    response = await _change(client, old_token, ALICE_PW, new_pw)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["ok"] is True

    # OLD password authentication fails after the change…
    old_login = await _login(client, ALICE_USERNAME, ALICE_PW)
    assert old_login.status_code == 401
    assert old_login.json()["success"] is False
    # …NEW password authenticates (fresh token resolves to the same identity).
    new_login = await _login(client, ALICE_USERNAME, new_pw)
    assert new_login.status_code == 200
    assert new_login.json()["data"]["user_id"] == alice_id

    # The pre-change token is revoked (Guard-03): protected route → 401.
    revoked = await client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {old_token}"}
    )
    assert revoked.status_code == 401
    assert revoked.json()["success"] is False


async def test_change_password_stored_hash_never_plaintext(
    seeded_app: tuple[AsyncEngine, dict[str, str]], client: httpx.AsyncClient
) -> None:
    """PASSWORD_HASH_STORAGE: only a salted scrypt hash is persisted."""
    token = await _token(client, ALICE_USERNAME, ALICE_PW)
    new_pw = "A-brand-new-password-2026!"
    response = await _change(client, token, ALICE_PW, new_pw)
    assert response.status_code == 200, response.text

    stored, _ = await _stored_hash(seeded_app[0], ALICE_USERNAME)
    assert stored is not None
    assert stored.startswith("$scrypt$")
    assert new_pw not in stored
    assert ALICE_PW not in stored
    # The hash round-trips through the existing verifier only for the new value.
    assert verify_password(new_pw, stored)
    assert not verify_password(ALICE_PW, stored)


async def test_change_other_user_password_impossible(
    seeded_app: tuple[AsyncEngine, dict[str, str]], client: httpx.AsyncClient
) -> None:
    """A token can never change another user's password.

    Even when alice knows bob's current password, submitting it via alice's
    token is rejected (the hash belongs to alice); and a body-supplied
    ``user_id`` targeting bob has no effect — bob's stored credential stays
    valid while only alice's own credential is what a valid call mutates.
    """
    bob_id = seeded_app[1]["bob"]
    alice_token = await _token(client, ALICE_USERNAME, ALICE_PW)
    bob_token = await _token(client, BOB_USERNAME, BOB_PW)
    bob_hash_before, bob_version_before = await _stored_hash(seeded_app[0], BOB_USERNAME)

    # (a) alice attempts to use bob's current password → REJECT.
    malicious_new = "Mallory-password-2026!"
    response = await _change(client, alice_token, BOB_PW, malicious_new)
    assert response.status_code == 400
    assert response.json()["success"] is False

    # (b) a body-supplied target user_id is ignored (target == principal).
    response = await _change(
        client,
        alice_token,
        ALICE_PW,
        "A-brand-new-password-2026!",
        user_id=bob_id,
        target_user_id=bob_id,
    )
    assert response.status_code == 200, response.text

    # bob is untouched: stored hash + token_version unchanged, both bob's old
    # credential and bob's pre-attempt token still authenticate.
    bob_hash_after, bob_version_after = await _stored_hash(seeded_app[0], BOB_USERNAME)
    assert bob_hash_after == bob_hash_before
    assert bob_version_after == bob_version_before
    bob_login = await _login(client, BOB_USERNAME, BOB_PW)
    assert bob_login.status_code == 200
    assert bob_login.json()["data"]["user_id"] == bob_id
    logout = await client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert logout.status_code == 200


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
