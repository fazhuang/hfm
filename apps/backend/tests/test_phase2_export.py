# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""Phase-2 P2-06 export/print tests.

Proves the frozen P2-06 acceptance criteria:
  - P2-06-AC-01 export output preserves the disclaimer (fixture assertion);
  - P2-06-AC-02 export of withdrawn content is blocked (fail-closed);
  - P2-06-AC-03 output is deterministic on fixture (no nondeterminism).
"""

from __future__ import annotations

import pytest

from hfm.phase2.export import (
    DISCLAIMER,
    ExportRecord,
    export_markdown,
    export_print,
)
from hfm.phase2.export.service import ExportError


def test_ac01_export_preserves_disclaimer() -> None:
    record = ExportRecord(
        title="《针灸甲乙经》校勘笔记",
        body="卷一引文与校勘说明。",
        publication_state="published",
    )
    markdown = export_markdown(record)
    assert DISCLAIMER in markdown
    print_artifact = export_print(record)
    assert DISCLAIMER in print_artifact


def test_ac02_withdrawn_export_blocked() -> None:
    record = ExportRecord(
        title="已撤回内容",
        body="不应导出。",
        publication_state="withdrawn",
    )
    with pytest.raises(ExportError):
        export_markdown(record)
    with pytest.raises(ExportError):
        export_print(record)


def test_ac02_draft_export_blocked() -> None:
    record = ExportRecord(
        title="草稿",
        body="不应导出。",
        publication_state="draft",
    )
    with pytest.raises(ExportError):
        export_markdown(record)


def test_ac03_deterministic_output() -> None:
    record = ExportRecord(
        title="固定标题",
        body="固定正文。",
        publication_state="published",
    )
    assert export_markdown(record) == export_markdown(record)
    assert export_print(record) == export_print(record)
    # identical inputs -> identical bytes (no timestamps, no randomness)
    assert export_markdown(record) == export_markdown(ExportRecord(record.title, record.body))
    assert len(export_markdown(record)) == len(export_markdown(record))
