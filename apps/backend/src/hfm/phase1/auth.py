"""HFM-native authentication / RBAC engine (P1-10 — ADR-07).

Default deny: an authenticated principal only has the permissions of its
roles; anonymous visitors have zero permissions. Credentials use a salted
KDF (hashlib.scrypt, stdlib — no new dependency); sessions are stateless
HMAC-signed tokens carrying sub/user_id, role, token_version and exp;
token_version is checked against the User row so logout/password-reset
immediately invalidates outstanding tokens (ADR-07 Guard-03).

No HFB user/password/session/RBAC state is migrated (NPG-8 MC-12); the
LocalDatabaseAuthProvider is the Phase 1 provider behind a pluggable
AuthProvider boundary (ADR-07 §4.4). Fail-closed token validation; default
denial.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.config import TOKEN_SECRET
from hfm.models.identity import (
    ROLE_PERMISSIONS,
    Role,
    User,
    UserRoleCode,
    role_permissions,
    user_roles,
)

#: signing secret from the single config source (ND-1 B01: production import
#: fails closed unless a real HFM_TOKEN_SECRET is present — see hfm.core.config).
_TOKEN_SECRET = TOKEN_SECRET
_TOKEN_TTL_SECONDS = 3600  # 1h
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1

#: Minimum password length — the SINGLE source for every HFM-managed
#: credential (self-service change AND the production first-admin bootstrap).
MIN_PASSWORD_LENGTH = 12

#: The SINGLE canonical list of passwords never acceptable as a real
#: credential (defaults, demo/test values, trivial sequences). Both the
#: runtime change-password path and the production bootstrap initializer
#: derive their accept/reject decision from this list and from
#: password_policy_reasons() below — no consumer maintains its own copy.
FORBIDDEN_PASSWORDS: frozenset[str] = frozenset(
    {
        "password",
        "changeme",
        "changeme123",
        "admin",
        "admin123",
        "secret",
        "hfm",
        "123456",
        "12345678",
        "123456789",
        "1234567890",
        "12345",
        "qwerty",
        "qwerty123",
        "letmein",
        "welcome",
        "iloveyou",
        "abc123",
        "111111",
        "000000",
    }
)

#: Stable policy-violation codes — the single accept/reject vocabulary shared
#: by the runtime and the production bootstrap. Display wording may differ per
#: consumer, but whether a password is accepted is decided HERE.
PW_REQUIRED = "required"
PW_TOO_SHORT = "too-short"
PW_FORBIDDEN_DEFAULT = "forbidden-default"
PW_CONTAINS_USERNAME = "contains-username"

#: Runtime (HTTP) wording for each violation code (display only).
_PW_RUNTIME_MESSAGES: dict[str, str] = {
    PW_REQUIRED: "a new password is required",
    PW_TOO_SHORT: f"password must be at least {MIN_PASSWORD_LENGTH} characters",
    PW_FORBIDDEN_DEFAULT: "password is a known default or demo value",
    PW_CONTAINS_USERNAME: "password must not contain the username",
}


def password_policy_reasons(password: str, *, username: str | None = None) -> list[str]:
    """Return the stable policy-violation codes (empty == policy satisfied).

    Single source of truth for accept/reject semantics. Runtime
    (change-own-password) and the production bootstrap initializer both call
    this function; consumers only map the returned codes to their own display
    wording. A caller-level rule such as "must differ from the current
    password" is applied by the caller on top of this credential policy.
    """
    reasons: list[str] = []
    if not password:
        reasons.append(PW_REQUIRED)
        return reasons
    if len(password) < MIN_PASSWORD_LENGTH:
        reasons.append(PW_TOO_SHORT)
    lowered = password.lower()
    if lowered in FORBIDDEN_PASSWORDS:
        reasons.append(PW_FORBIDDEN_DEFAULT)
    if username and username.lower() in lowered:
        reasons.append(PW_CONTAINS_USERNAME)
    return reasons


def password_policy_errors(password: str, *, username: str | None = None) -> list[str]:
    """Human-readable policy violations (runtime HTTP detail; display only).

    Accept/reject semantics come from password_policy_reasons(); this function
    only renders the codes for the change-own-password endpoint.
    """
    return [
        _PW_RUNTIME_MESSAGES[reason]
        for reason in password_policy_reasons(password, username=username)
    ]


@dataclass(frozen=True)
class Principal:
    """Authenticated principal (or anonymous)."""

    user_id: str | None
    roles: tuple[str, ...]
    permissions: frozenset[str]

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    def has_permission(self, code: str) -> bool:
        return code in self.permissions


ANONYMOUS = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())


def hash_password(password: str, salt: bytes | None = None) -> str:
    """Salted scrypt hash: $scrypt$<salt-b64>$<hash-b64>."""
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P
    )
    return f"$scrypt${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) != 4 or parts[1] != "scrypt":
        return False
    try:
        salt = base64.b64decode(parts[2])
        expected = base64.b64decode(parts[3])
    except (ValueError, TypeError):
        return False
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P
    )
    return hmac.compare_digest(digest, expected)


def _expiry_ts() -> int:
    """Token expiry unix seconds (defensive; time never fails but stays guarded)."""
    try:
        return int(time.time()) + _TOKEN_TTL_SECONDS
    except (OverflowError, ValueError, OSError):  # pragma: no cover - defensive
        return int(time.time())


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def issue_token(user_id: str, role: str, token_version: int) -> str:
    """Stateless signed token: base64url(header).base64url(payload).sig."""
    header = _b64url(json.dumps({"alg": "HS256", "typ": "HFM-JWT"}).encode())
    payload = _b64url(
        json.dumps(
            {
                "sub": user_id,
                "role": role,
                "token_version": token_version,
                "exp": _expiry_ts(),
            },
            separators=(",", ":"),
        ).encode()
    )
    signing_input = f"{header}.{payload}".encode()
    sig = _b64url(hmac.new(_TOKEN_SECRET.encode(), signing_input, hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


def parse_token(token: str) -> dict[str, object] | None:
    """Return the payload when the signature is valid; None otherwise."""
    try:
        header, payload, sig = token.split(".")
        signing_input = f"{header}.{payload}".encode()
        expected = _b64url(hmac.new(_TOKEN_SECRET.encode(), signing_input, hashlib.sha256).digest())
        if not hmac.compare_digest(expected, sig):
            return None
        body = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if int(str(body.get("exp", 0))) < int(time.time()):
            return None
        return body if isinstance(body, dict) else None
    except (ValueError, json.JSONDecodeError, TypeError):
        return None


async def ensure_roles_seeded(session: AsyncSession) -> None:
    """Seed the frozen 5 roles + role→permission matrix (idempotent)."""
    existing = {r.code for r in (await session.execute(select(Role))).scalars().all()}
    for code in UserRoleCode:
        if code.value not in existing:
            role = Role(code=code.value, name=code.name)
            session.add(role)
            await session.flush()
            for perm in ROLE_PERMISSIONS[code]:
                await session.execute(
                    role_permissions.insert().values(role_id=role.id, permission_code=perm)
                )
    await session.flush()


async def permissions_for_user(session: AsyncSession, user_id: str) -> frozenset[str]:
    """Permissions of a user across all roles (default deny: empty for none)."""
    role_codes = (
        (
            await session.execute(
                select(Role.code)
                .join(user_roles, user_roles.c.role_id == Role.id)
                .where(user_roles.c.user_id == user_id)
            )
        )
        .scalars()
        .all()
    )
    perms: set[str] = set()
    for code in role_codes:
        try:
            perms |= set(ROLE_PERMISSIONS[UserRoleCode(code)])
        except ValueError:
            continue
    return frozenset(perms)


async def principal_for_token(session: AsyncSession, token: str | None) -> Principal:
    """Resolve a token to a Principal; invalid/expired/missing → anonymous
    (default deny — the caller decides whether authentication is required)."""
    if not token:
        return ANONYMOUS
    body = parse_token(token)
    if body is None:
        return ANONYMOUS
    user = await session.get(User, str(body.get("sub", "")))
    if user is None or not user.is_active:
        return ANONYMOUS
    try:
        token_version = int(str(body.get("token_version", -1)))
    except (ValueError, TypeError):
        return ANONYMOUS  # malformed token_version fails closed
    if user.token_version != token_version:
        return ANONYMOUS  # token revoked (logout/password change — Guard-03)
    roles = (
        (
            await session.execute(
                select(Role.code)
                .join(user_roles, user_roles.c.role_id == Role.id)
                .where(user_roles.c.user_id == user.id)
            )
        )
        .scalars()
        .all()
    )
    return Principal(
        user_id=user.id,
        roles=tuple(roles) or ("ANONYMOUS_VISITOR",),
        permissions=await permissions_for_user(session, user.id),
    )
