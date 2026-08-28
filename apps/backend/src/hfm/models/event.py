"""Event model (CD-6 — NEW, CA-004).

HFM-native per Frozen Canonical Model §1/§2: Event is a NEW aggregate
"基于 Assertion 聚合" — the event's stable identity lives on its CD-1
Entity row (entity_type='event', shared stable identity backbone I5), and
the event's historical FACTS are the Assertions aggregated to it (claim
layer), never single-truth columns (Assertion Contract §14 boundary).

This table holds only canonical research metadata:
  - event_type (typed canonical anchor);
  - a canonical temporal FRAME (start/end with per-bound precision
    unknown/year/month/day + approximate flags) — a research envelope,
    NOT a truth claim; contested dates coexist as aggregated Assertions
    (I3) and revisions are new Assertions (I4).

Frozen scope gates: 时间区间 (temporal range with start<=end, §16) and
full precision support — year/month/day/approximate/range/unknown (§15),
never reduced to a single datetime column.
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
from sqlalchemy import (
    event as sa_event,
)
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import Base, BaseModel


class EventType(enum.StrEnum):
    """Canonical event families (HFM-native; life events per Scope v0.1 §6.1)."""

    birth = "birth"
    death = "death"
    study = "study"
    career = "career"
    marriage = "marriage"
    travel = "travel"
    composition = "composition"
    meeting = "meeting"
    other = "other"


class EventBoundPrecision(enum.StrEnum):
    """Temporal precision of one bound (unknown/year/month/day — §15)."""

    unknown = "unknown"
    year = "year"
    month = "month"
    day = "day"


_EVENT_TYPE_VALUES = ", ".join(f"'{t.value}'" for t in EventType)
_PRECISION_VALUES = ", ".join(f"'{p.value}'" for p in EventBoundPrecision)

#: precision → the (year, month, day) nullability pattern required.
_PRECISION_PATTERN = {
    EventBoundPrecision.unknown: (False, False, False),
    EventBoundPrecision.year: (True, False, False),
    EventBoundPrecision.month: (True, True, False),
    EventBoundPrecision.day: (True, True, True),
}


def validate_event_frame(
    *,
    start_year: int | None,
    start_month: int | None,
    start_day: int | None,
    start_precision: EventBoundPrecision,
    end_year: int | None,
    end_month: int | None,
    end_day: int | None,
    end_precision: EventBoundPrecision,
) -> None:
    """Validate the canonical temporal frame (consistency + ranges + order)."""
    for label, (y, m, d, p) in (
        ("start", (start_year, start_month, start_day, start_precision)),
        ("end", (end_year, end_month, end_day, end_precision)),
    ):
        year_req, month_req, day_req = _PRECISION_PATTERN[p]
        if (y is None) == year_req:
            raise ValueError(
                f"event {label}_precision={p.value} requires year="
                f"{'present' if year_req else 'absent'} (got {y!r})"
            )
        if (m is None) == month_req:
            raise ValueError(
                f"event {label}_precision={p.value} requires month="
                f"{'present' if month_req else 'absent'} (got {m!r})"
            )
        if (d is None) == day_req:
            raise ValueError(
                f"event {label}_precision={p.value} requires day="
                f"{'present' if day_req else 'absent'} (got {d!r})"
            )
        if m is not None and not 1 <= m <= 12:
            raise ValueError(f"event {label}_month must be 1..12 (got {m})")
        if d is not None and not 1 <= d <= 31:
            raise ValueError(f"event {label}_day must be 1..31 (got {d})")
        if y is not None and not -9999 <= y <= 9999:
            raise ValueError(f"event {label}_year must be within -9999..9999 (got {y})")
    # start <= end (open intervals allowed: either bound unknown)
    if start_year is not None and end_year is not None:
        start = (start_year, start_month or 1, start_day or 1)
        end = (end_year, end_month or 1, end_day or 1)
        if start > end:
            raise ValueError(f"event start must not be after end ({start} > {end})")


class Event(BaseModel):
    """A life-event aggregate with a canonical temporal frame (CD-6 — NEW)."""

    __tablename__ = "events"
    #: typed-Entity identity: entity_id 1:1 → entities.id (UNIQUE, NOT NULL).
    #: the row keeps the BaseModel UUIDv7 surrogate PK (standard model shape)
    #: while the UNIQUE entity_id is the semantic identity and the FK target
    #: for event_relations / event_assertions.
    __table_args__ = (
        UniqueConstraint("entity_id", name="uq_events_entity_id"),
        CheckConstraint(
            f"event_type IN ({_EVENT_TYPE_VALUES})",
            name="ck_events_event_type",
        ),
        CheckConstraint(
            f"start_precision IN ({_PRECISION_VALUES})",
            name="ck_events_start_precision",
        ),
        CheckConstraint(
            f"end_precision IN ({_PRECISION_VALUES})",
            name="ck_events_end_precision",
        ),
        CheckConstraint(
            "(start_precision = 'unknown' AND start_year IS NULL"
            " AND start_month IS NULL AND start_day IS NULL)"
            " OR (start_precision = 'year' AND start_year IS NOT NULL"
            " AND start_month IS NULL AND start_day IS NULL)"
            " OR (start_precision = 'month' AND start_year IS NOT NULL"
            " AND start_month IS NOT NULL AND start_day IS NULL)"
            " OR (start_precision = 'day' AND start_year IS NOT NULL"
            " AND start_month IS NOT NULL AND start_day IS NOT NULL)",
            name="ck_events_start_consistency",
        ),
        CheckConstraint(
            "(end_precision = 'unknown' AND end_year IS NULL"
            " AND end_month IS NULL AND end_day IS NULL)"
            " OR (end_precision = 'year' AND end_year IS NOT NULL"
            " AND end_month IS NULL AND end_day IS NULL)"
            " OR (end_precision = 'month' AND end_year IS NOT NULL"
            " AND end_month IS NOT NULL AND end_day IS NULL)"
            " OR (end_precision = 'day' AND end_year IS NOT NULL"
            " AND end_month IS NOT NULL AND end_day IS NOT NULL)",
            name="ck_events_end_consistency",
        ),
        CheckConstraint(
            "(start_month IS NULL OR start_month BETWEEN 1 AND 12)"
            " AND (end_month IS NULL OR end_month BETWEEN 1 AND 12)",
            name="ck_events_month_range",
        ),
        CheckConstraint(
            "(start_day IS NULL OR start_day BETWEEN 1 AND 31)"
            " AND (end_day IS NULL OR end_day BETWEEN 1 AND 31)",
            name="ck_events_day_range",
        ),
        CheckConstraint(
            "(start_year IS NULL OR start_year BETWEEN -9999 AND 9999)"
            " AND (end_year IS NULL OR end_year BETWEEN -9999 AND 9999)",
            name="ck_events_year_range",
        ),
        CheckConstraint(
            "start_year IS NULL OR end_year IS NULL"
            " OR (start_year, COALESCE(start_month, 1), COALESCE(start_day, 1))"
            " <= (end_year, COALESCE(end_month, 1), COALESCE(end_day, 1))",
            name="ck_events_start_le_end",
        ),
    )

    #: identity + canonical temporal frame are immutable (I4): contested
    #: dates are new/aggregated Assertions, never a silent frame overwrite.
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "id",
            "entity_id",
            "event_type",
            "start_year",
            "start_month",
            "start_day",
            "start_precision",
            "start_approximate",
            "end_year",
            "end_month",
            "end_day",
            "end_precision",
            "end_approximate",
        }
    )

    @validates(
        "entity_id",
        "event_type",
        "start_year",
        "start_month",
        "start_day",
        "start_precision",
        "start_approximate",
        "end_year",
        "end_month",
        "end_day",
        "end_precision",
        "end_approximate",
    )
    def _validate_immutable_anchor(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # loaded-state guard: once the column is materialized (constructed or
        # reloaded), any change from the current value is rejected (identity +
        # canonical frame are immutable — I4). Event has no surrogate id
        # column, so __dict__ membership marks the persisted/assigned state.
        if key in self.__dict__ and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new event")
        return value

    entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        comment="稳定标识（= entities.id，1:1 UNIQUE；EntityType.event，I5）",
    )
    event_type: Mapped[EventType] = mapped_column(
        String(30),
        nullable=False,
        comment="事件类型（canonical anchor）",
    )
    start_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="起始年（帧；非真值主张）"
    )
    start_month: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="起始月")
    start_day: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="起始日")
    start_precision: Mapped[EventBoundPrecision] = mapped_column(
        String(20),
        nullable=False,
        default=EventBoundPrecision.unknown,
        server_default="unknown",
        comment="起始边界精度: unknown/year/month/day",
    )
    start_approximate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="起始约数（circa）标志",
    )
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="结束年")
    end_month: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="结束月")
    end_day: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="结束日")
    end_precision: Mapped[EventBoundPrecision] = mapped_column(
        String(20),
        nullable=False,
        default=EventBoundPrecision.unknown,
        server_default="unknown",
        comment="结束边界精度: unknown/year/month/day",
    )
    end_approximate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="结束约数（circa）标志",
    )


event_assertions = Table(
    "event_assertions",
    Base.metadata,
    Column(
        "event_id",
        String(36),
        ForeignKey("events.entity_id", ondelete="CASCADE"),
        primary_key=True,
        comment="事件（= entities.id）",
    ),
    Column(
        "assertion_id",
        String(36),
        ForeignKey("assertions.id", ondelete="CASCADE"),
        primary_key=True,
        comment="聚合主张（CD-4）",
    ),
)


#: SQLite-only backstop: the event domain boundary requires every aggregated
#: Assertion to have subject_entity_id == event_id (Frozen CD-6 scope —
#: event evidence aggregate = assertions ABOUT the event). A CHECK cannot
#: express the join, so an insert trigger enforces it at the DB layer (§35
#: strong-probe pattern); the repository raises ValueError first. PostgreSQL
#: relies on the repository guard (no portable trigger).
def _create_aggregation_trigger(target: object, connection: Connection, **kw: object) -> None:
    connection.exec_driver_sql(
        "CREATE TRIGGER IF NOT EXISTS trg_event_assertions_subject_match"
        " BEFORE INSERT ON event_assertions"
        " FOR EACH ROW"
        " WHEN NOT EXISTS (SELECT 1 FROM assertions"
        "   WHERE id = NEW.assertion_id AND subject_entity_id = NEW.event_id)"
        " BEGIN SELECT RAISE(ABORT, 'event_assertions subject mismatch'); END"
    )


sa_event.listen(event_assertions, "after_create", _create_aggregation_trigger)
