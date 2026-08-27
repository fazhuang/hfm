"""HFM database foundation (CD-0).

ADAPT of HFB `apps/backend/app/db/base.py` @ `03755b5`:
  - retained: DeclarativeBase + TimestampMixin (created_at/updated_at);
  - removed: SoftDeleteMixin (not required by CD-0 canonical scope);
  - identifiers moved to `hfm.core.identifiers`.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from hfm.core.identifiers import uuid7


class Base(DeclarativeBase):
    """Base class for all HFM database models."""


class TimestampMixin:
    """Mixin adding created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """Base model with a UUIDv7 primary key and timestamps."""

    __abstract__ = True

    #: Fields that repositories must never update (I5 stable identity).
    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id"})

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uuid7,
        comment="稳定标识（UUIDv7）",
    )
