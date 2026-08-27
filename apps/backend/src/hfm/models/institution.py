"""Institution model (CD-0 — REUSE).

REUSE of HFB `models/institution.py` (CA-005) @ `03755b5`:
  - retained: name / type / location / description / status fields and
    enums (InstitutionType, InstitutionStatus);
  - removed: dependency on the HFB status-machine service module (the enum
    states are retained; transition enforcement is a service-layer concern
    for later batches);
  - rewritten: HFM namespace + `native_enum=False` for SQLite/PG parity.
"""

from __future__ import annotations

import enum

from sqlalchemy import CheckConstraint, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class InstitutionType(enum.StrEnum):
    """Valid institution types."""

    research = "research"
    university = "university"
    archive = "archive"
    institution = "institution"


class InstitutionStatus(enum.StrEnum):
    """Institution lifecycle states (state-machine transitions deferred to service layer)."""

    draft = "draft"
    active = "active"
    archived = "archived"
    deleted = "deleted"


class Institution(BaseModel):
    """An organization relevant to HFM studies (universities, institutes, archives)."""

    __tablename__ = "institutions"
    __table_args__ = (
        CheckConstraint(
            "type IN ('research', 'university', 'archive', 'institution')",
            name="ck_institutions_type",
        ),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived', 'deleted')",
            name="ck_institutions_status",
        ),
    )

    name: Mapped[str] = mapped_column(String(300), nullable=False, comment="机构名称")
    type: Mapped[InstitutionType] = mapped_column(
        Enum(InstitutionType, native_enum=False, length=30),
        nullable=False,
        default=InstitutionType.institution,
        comment="机构类型",
    )
    location: Mapped[str | None] = mapped_column(String(300), nullable=True, comment="所在地")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="机构描述")
    status: Mapped[InstitutionStatus] = mapped_column(
        Enum(InstitutionStatus, native_enum=False, length=30),
        nullable=False,
        default=InstitutionStatus.draft,
        comment="机构状态",
    )
