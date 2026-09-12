"""Reconciliation run model (P1-13 — batch metrics + PASS/FAIL recorded).

Each run records the deterministic expected metrics (count + canonical
digest) and the observed metrics for a governed scope; the status is
PASS only when both match. Rows are append-only: the recorded metrics are
immutable evidence (E-13) and cannot be silently amended.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class ReconciliationStatus(enum.StrEnum):
    """Reconciliation outcome (PASS only when metrics match exactly)."""

    PASS = "PASS"
    FAIL = "FAIL"


class ReconciliationRun(BaseModel):
    """One recorded reconciliation result for a governed scope (P1-13)."""

    __tablename__ = "reconciliation_runs"
    __table_args__ = (
        CheckConstraint("status IN ('PASS', 'FAIL')", name="ck_reconciliation_runs_status"),
        CheckConstraint(
            "expected_count >= 0 AND actual_count >= 0", name="ck_reconciliation_runs_counts"
        ),
        CheckConstraint("length(scope) > 0", name="ck_reconciliation_runs_scope_present"),
        CheckConstraint(
            "length(expected_hash) = 64 AND length(actual_hash) = 64",
            name="ck_reconciliation_runs_hashes",
        ),
    )

    #: the entire run is immutable evidence — append-only (I4).
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "id",
            "scope",
            "expected_count",
            "expected_hash",
            "actual_count",
            "actual_hash",
            "status",
            "checked_at",
            "created_by",
        }
    )

    @validates(
        "scope",
        "expected_count",
        "expected_hash",
        "actual_count",
        "actual_hash",
        "status",
        "checked_at",
        "created_by",
    )
    def _validate_immutable(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # id-based guard: once persisted, any change from the loaded state is
        # rejected — recorded reconciliation evidence cannot be rewritten.
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): reconciliation runs are append-only")
        return value

    scope: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="治理范围（table:<name> 或 batch:<id>）"
    )
    expected_count: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="期望行数（批次清单）"
    )
    expected_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="期望规范化摘要（sha256）"
    )
    actual_count: Mapped[int] = mapped_column(Integer, nullable=False, comment="实测行数")
    actual_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="实测规范化摘要（sha256）"
    )
    status: Mapped[ReconciliationStatus] = mapped_column(
        String(10),
        nullable=False,
        comment="PASS（指标完全一致）/ FAIL（失配，fail-closed）",
    )
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="对账时间",
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36), nullable=True, comment="触发者（users.id 或 NULL）"
    )
