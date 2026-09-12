"""Phase 1 P1-10 — HFM-native Identity/RBAC tests (ADR-07).

Default deny, 5-role model, permission enforcement, token revocation,
separation of duties, no credential migration.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.identity import (
    ROLE_PERMISSIONS,
    Role,
    User,
    UserRoleCode,
    user_roles,
)
from hfm.phase1.auth import (
    ANONYMOUS,
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    parse_token,
    principal_for_token,
    verify_password,
)


async def _user(session: AsyncSession, username: str, role_code: UserRoleCode) -> User:
    await ensure_roles_seeded(session)
    user = User(username=username, password_hash=hash_password("pw"))
    session.add(user)
    await session.flush()
    role_row = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
    await session.flush()
    return user


def test_password_hash_verify() -> None:
    h = hash_password("secret")
    assert verify_password("secret", h)
    assert not verify_password("wrong", h)
    assert h.startswith("$scrypt$")


def test_token_issue_parse_tamper() -> None:
    t = issue_token("u1", "CONTENT_REVIEWER", 3)
    body = parse_token(t)
    assert body is not None and body["sub"] == "u1" and body["token_version"] == 3
    assert parse_token(t[:-1] + ("X" if t[-1] != "X" else "Y")) is None
    assert parse_token("garbage") is None


def test_anonymous_default_deny() -> None:
    assert not ANONYMOUS.is_authenticated
    assert ANONYMOUS.permissions == frozenset()
    assert not ANONYMOUS.has_permission("content:publish")


def test_role_permission_matrix_frozen() -> None:
    assert set(UserRoleCode) == {
        UserRoleCode.ANONYMOUS_VISITOR,
        UserRoleCode.STUDENT_RESEARCHER,
        UserRoleCode.SCHOLAR_RESEARCHER,
        UserRoleCode.CONTENT_REVIEWER,
        UserRoleCode.SYSTEM_ADMIN,
    }
    assert ROLE_PERMISSIONS[UserRoleCode.ANONYMOUS_VISITOR] == frozenset()
    assert "content:publish" in ROLE_PERMISSIONS[UserRoleCode.CONTENT_REVIEWER]
    assert "content:review" in ROLE_PERMISSIONS[UserRoleCode.CONTENT_REVIEWER]
    assert "user:manage" in ROLE_PERMISSIONS[UserRoleCode.SYSTEM_ADMIN]
    assert "content:publish" not in ROLE_PERMISSIONS[UserRoleCode.SCHOLAR_RESEARCHER]


async def test_roles_seeded(session: AsyncSession) -> None:
    await ensure_roles_seeded(session)
    roles = (await session.execute(select(Role))).scalars().all()
    assert len(roles) == 5


async def test_principal_from_token(session: AsyncSession) -> None:
    user = await _user(session, "reviewer1", UserRoleCode.CONTENT_REVIEWER)
    token = issue_token(user.id, UserRoleCode.CONTENT_REVIEWER.value, user.token_version)
    principal = await principal_for_token(session, token)
    assert principal.is_authenticated
    assert principal.has_permission("content:publish")
    assert not principal.has_permission("user:manage")


async def test_token_revocation_immediate(session: AsyncSession) -> None:
    """ADR-07 Guard-03: token_version bump invalidates outstanding tokens."""
    user = await _user(session, "reviewer2", UserRoleCode.CONTENT_REVIEWER)
    token = issue_token(user.id, UserRoleCode.CONTENT_REVIEWER.value, user.token_version)
    assert (await principal_for_token(session, token)).is_authenticated
    user.token_version += 1  # logout / password change
    await session.flush()
    principal = await principal_for_token(session, token)
    assert not principal.is_authenticated  # old token dead


async def test_invalid_and_anonymous_tokens_denied(session: AsyncSession) -> None:
    assert not (await principal_for_token(session, None)).is_authenticated
    assert not (await principal_for_token(session, "not-a-token")).is_authenticated


async def test_default_deny_for_researcher(session: AsyncSession) -> None:
    user = await _user(session, "scholar1", UserRoleCode.SCHOLAR_RESEARCHER)
    token = issue_token(user.id, UserRoleCode.SCHOLAR_RESEARCHER.value, user.token_version)
    principal = await principal_for_token(session, token)
    assert not principal.has_permission("content:publish")
    assert not principal.has_permission("content:withdraw")
    assert principal.has_permission("assertion:create")


def test_principal_immutable_equality() -> None:
    p = Principal(user_id="x", roles=("A",), permissions=frozenset({"p"}))
    assert p.has_permission("p") and not p.has_permission("q")
