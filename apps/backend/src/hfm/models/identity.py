"""HFM-native identity models (P1-10 — ADR-07).

HFM owns identity and authorization (AB-08 / ADR-07). The 5-role model is
frozen: ANONYMOUS_VISITOR / STUDENT_RESEARCHER / SCHOLAR_RESEARCHER /
CONTENT_REVIEWER / SYSTEM_ADMIN. Credentials use a salted KDF (hashlib.scrypt,
stdlib — no new dependency); sessions are stateless signed tokens with a
token_version for immediate revocation. No HFB user/password/session/RBAC
data is migrated (NPG-8 MC-12).
"""

from __future__ import annotations

import enum
from typing import ClassVar

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import Base, BaseModel


class UserRoleCode(enum.StrEnum):
    """Frozen 5-role model (ADR-07 §4.1)."""

    ANONYMOUS_VISITOR = "ANONYMOUS_VISITOR"
    STUDENT_RESEARCHER = "STUDENT_RESEARCHER"
    SCHOLAR_RESEARCHER = "SCHOLAR_RESEARCHER"
    CONTENT_REVIEWER = "CONTENT_REVIEWER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


_ROLE_VALUES = ", ".join(f"'{r.value}'" for r in UserRoleCode)

#: Frozen atomic permission codes (ADR-07 §4.2).
PERMISSION_CODES: tuple[str, ...] = (
    "assertion:create",
    "project:create",
    "content:review",
    "content:publish",
    "content:withdraw",
    "user:manage",
    "audit:read",
)

#: role → permissions (default deny: a role has exactly these permissions).
ROLE_PERMISSIONS: dict[UserRoleCode, frozenset[str]] = {
    UserRoleCode.ANONYMOUS_VISITOR: frozenset(),
    UserRoleCode.STUDENT_RESEARCHER: frozenset({"assertion:create", "project:create"}),
    UserRoleCode.SCHOLAR_RESEARCHER: frozenset({"assertion:create", "project:create"}),
    UserRoleCode.CONTENT_REVIEWER: frozenset(
        {"content:review", "content:publish", "content:withdraw"}
    ),
    UserRoleCode.SYSTEM_ADMIN: frozenset(PERMISSION_CODES),
}

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_code", String(60), primary_key=True),
)


class User(BaseModel):
    """HFM-native account (canonical identity; no HFB credential migration)."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        CheckConstraint("is_active IN (0, 1)", name="ck_users_is_active"),
    )

    #: password_hash and roles are managed via the auth service; username is
    #: immutable after creation (stable identity — I5/I4).
    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "username"})

    @validates("username")
    def _validate_username(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError("username is immutable (I4)")
        return value

    username: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="登录名（canonical）"
    )
    password_hash: Mapped[str] = mapped_column(
        String(256), nullable=False, comment="加盐 KDF 哈希（scrypt；不存明文）"
    )
    token_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0", comment="JWT 即时撤销版本"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", comment="账号启用"
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36), nullable=True, comment="创建者（SYSTEM_ADMIN user id 或 NULL）"
    )


class Role(BaseModel):
    """A frozen role (5-role model, ADR-07 §4.1)."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("code", name="uq_roles_code"),
        CheckConstraint(
            f"code IN ({_ROLE_VALUES})",
            name="ck_roles_code",
        ),
    )

    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "code"})

    @validates("code")
    def _validate_code(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError("role code is immutable (I4)")
        return value

    code: Mapped[UserRoleCode] = mapped_column(
        String(30), nullable=False, comment="角色代码（ADR-07 5 角色）"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="角色名称")
