"""Export service (P2-06 — P2-C6 export/print, G9 disclaimer retention).

Serializes research/public records to markdown (and a print artifact) with
the mandatory historical-research disclaimer always retained. Withdrawn
content is rejected fail-closed. All outputs are deterministic pure
functions of their inputs (P2-06-AC-03).
"""

from __future__ import annotations

from dataclasses import dataclass

#: Historical-research disclaimer (G9) — retained in every export output.
DISCLAIMER = (
    "本文为历史文献研究内容，仅供学术研究；不构成任何诊断、治疗、"
    "用药或穴位操作建议。"
)

#: Publication states that may never be exported.
BLOCKED_STATES: frozenset[str] = frozenset({"withdrawn", "draft"})


@dataclass(frozen=True)
class ExportRecord:
    """One exportable record (title + body + publication state)."""

    title: str
    body: str
    publication_state: str = "published"


class ExportError(ValueError):
    """Raised when a record cannot be exported (fail-closed)."""


def _assert_exportable(record: ExportRecord) -> None:
    if record.publication_state in BLOCKED_STATES:
        raise ExportError(
            f"cannot export {record.publication_state} content: {record.title}"
        )


def export_markdown(record: ExportRecord) -> str:
    """Deterministic markdown export with the disclaimer always retained."""
    _assert_exportable(record)
    return "\n".join(
        [
            f"# {record.title}",
            "",
            record.body,
            "",
            f"> {DISCLAIMER}",
            "",
        ]
    )


def export_print(record: ExportRecord) -> str:
    """Deterministic print artifact (plain text, disclaimer retained)."""
    _assert_exportable(record)
    return "\n".join(
        [
            record.title,
            "=" * len(record.title),
            record.body,
            "",
            DISCLAIMER,
            "",
        ]
    )
