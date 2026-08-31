"""HFM Phase 2 export & print (P2-06).

Markdown (and print) export with mandatory disclaimer retention (G9).
Withdrawn or private content can never be exported (fail-closed). Output
is deterministic: identical input produces identical bytes (P2-06-AC-03).
PDF export is not enabled in this implementation; the frozen criterion is
conditional ("if enabled") and the deterministic markdown/print artifacts
satisfy the deterministic-output requirement.
"""

from __future__ import annotations

from hfm.phase2.export.service import DISCLAIMER, ExportRecord, export_markdown, export_print

__all__ = ["DISCLAIMER", "ExportRecord", "export_markdown", "export_print"]
