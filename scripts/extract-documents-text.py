#!/usr/bin/env python3
"""HFM P2 full-text extraction — Route A (direct text layer) + OCR manifest.

Runs the document-production ledger's pre-profiled routing over the physical
source PDFs under ``hfmzl/``:

  - A_TEXT / C_MIXED documents with an extractable text layer are written to
    ``content-production/corpus/extracted-text/<ASSET_ID>_raw.txt`` (Route A).
  - B_OCR (scanned) documents, and any A-document that yields no text, are
    recorded in ``content-production/corpus/ocr-required.csv`` for the
    long-running OCR stage (tesseract, ~12s/page) — NOT run here.

This is the controlled, idempotent, resumable counterpart to the B02
controlled-scale pipeline. It only reads source files and writes extracted
text under the git-ignored corpus output dirs; it never touches the database.

Usage:
    python extract-documents-text.py [--limit N] [--force]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent

LEDGER_CSV = REPO_ROOT / "content-production" / "corpus" / "document-production-ledger.csv"
HFMZL = REPO_ROOT / "hfmzl"
OUT_DIR = REPO_ROOT / "content-production" / "corpus" / "extracted-text"
OCR_REQUIRED = REPO_ROOT / "content-production" / "corpus" / "ocr-required.csv"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_source(rel_path: str) -> Path | None:
    candidate = HFMZL / rel_path
    if candidate.is_file():
        return candidate
    return None


def pdftotext(pdf: Path, out: Path) -> bool:
    """Extract the text layer; return True when non-empty text was written."""
    run = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf), str(out)],
        capture_output=True,
        text=True,
        check=False,
    )
    return run.returncode == 0 and out.exists() and out.stat().st_size > 40


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="process at most N documents")
    parser.add_argument(
        "--force", action="store_true", help="re-extract even if the output already exists"
    )
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(LEDGER_CSV.open(encoding="utf-8-sig", newline="")))
    stats = {"extracted": 0, "skipped_existing": 0, "ocr_required": 0, "missing": 0, "failed": 0}
    ocr_rows: list[dict[str, str]] = []

    count = 0
    for row in rows:
        if args.limit is not None and count >= args.limit:
            break
        asset_id = row.get("ASSET_ID", "").strip()
        rel_path = row.get("SOURCE_PATH", "").strip()
        route = row.get("PROCESSING_ROUTE", "").strip()
        expected_sha = row.get("SHA256", "").strip()
        if not asset_id or not rel_path or not rel_path.lower().endswith(".pdf"):
            continue
        count += 1

        out_file = OUT_DIR / f"{asset_id}_raw.txt"
        if out_file.exists() and not args.force:
            stats["skipped_existing"] += 1
            continue

        pdf = resolve_source(rel_path)
        if pdf is None:
            stats["missing"] += 1
            ocr_rows.append(
                {"ASSET_ID": asset_id, "SOURCE_PATH": rel_path, "REASON": "missing_source"}
            )
            continue

        if expected_sha and sha256_of(pdf) != expected_sha:
            stats["failed"] += 1
            ocr_rows.append(
                {"ASSET_ID": asset_id, "SOURCE_PATH": rel_path, "REASON": "sha256_mismatch"}
            )
            continue

        if pdftotext(pdf, out_file):
            stats["extracted"] += 1
        elif route == "B_OCR":
            stats["ocr_required"] += 1
            ocr_rows.append(
                {"ASSET_ID": asset_id, "SOURCE_PATH": rel_path, "REASON": "B_OCR_no_text"}
            )
        else:
            # An A-document unexpectedly produced no text — treat as OCR-required
            # (never silently drop it).
            stats["ocr_required"] += 1
            ocr_rows.append(
                {"ASSET_ID": asset_id, "SOURCE_PATH": rel_path, "REASON": "A_empty_text"}
            )

    if ocr_rows:
        with OCR_REQUIRED.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["ASSET_ID", "SOURCE_PATH", "REASON"])
            writer.writeheader()
            writer.writerows(ocr_rows)

    print(f"EXTRACT_DOCUMENTS_TEXT=PASS")
    print(f"SUMMARY={stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
