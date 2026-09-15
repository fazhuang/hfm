#!/usr/bin/env python3
"""HFM P2 full-text extraction — Route B (OCR) for scanned documents.

Runs tesseract OCR over the scanned (image-layer) documents listed in
``content-production/corpus/ocr-required.csv``. Each page is rendered with
pdftoppm (300 dpi grayscale) then OCR'd with a language profile chosen from
the source path:

  - 论著 (classical editions)  -> chi_tra_vert  (vertical traditional)
  - 非遗佐证 (certificates)    -> chi_sim+eng
  - otherwise (scanned papers) -> chi_sim

Output is the RAW OCR layer (never treated as a verified transcription) under
``content-production/corpus/raw-ocr/<ASSET_ID>_raw.txt``. This is the
long-running stage (~12s/page); use --limit/--pages to sample first.

Usage:
    python extract-documents-ocr.py [--limit N] [--pages N]
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent

OCR_REQUIRED_CSV = REPO_ROOT / "content-production" / "corpus" / "ocr-required.csv"
HFMZL = REPO_ROOT / "hfmzl"
OUT_DIR = REPO_ROOT / "content-production" / "corpus" / "raw-ocr"

_DPI = 300


def language_for(path: str) -> str:
    if "非遗佐证" in path:
        return "chi_sim+eng"
    if "论著" in path:
        return "chi_tra_vert"
    return "chi_sim"


def ocr_page(pdf: Path, lang: str, page: int, tmp: Path) -> str:
    prefix = tmp / "page"
    render = subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(_DPI), "-gray",
         "-png", str(pdf), str(prefix)],
        capture_output=True,
        text=True,
        check=False,
    )
    if render.returncode != 0:
        return ""
    image = next(tmp.glob("page-*.png"), None)
    if image is None:
        return ""
    run = subprocess.run(
        ["tesseract", str(image), "-", "-l", lang],
        capture_output=True,
        text=True,
        check=False,
    )
    return run.stdout if run.returncode == 0 else ""


def page_count(pdf: Path) -> int:
    run = subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True, check=False
    )
    for line in run.stdout.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":")[1].strip())
            except (IndexError, ValueError):
                return 0
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="OCR at most N documents")
    parser.add_argument("--pages", type=int, default=None, help="OCR at most N pages per document")
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(OCR_REQUIRED_CSV.open(encoding="utf-8-sig", newline="")))

    stats = {"ocr_done": 0, "ocr_failed": 0, "pages": 0}
    count = 0
    for row in rows:
        if args.limit is not None and count >= args.limit:
            break
        asset_id = row.get("ASSET_ID", "").strip()
        rel_path = row.get("SOURCE_PATH", "").strip()
        pdf = HFMZL / rel_path
        if not asset_id or not pdf.is_file():
            continue
        count += 1

        total_pages = page_count(pdf)
        pages = min(total_pages, args.pages or total_pages)
        lang = language_for(rel_path)

        chunks: list[str] = []
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            for page in range(1, pages + 1):
                text = ocr_page(pdf, lang, page, tmp)
                if text.strip():
                    chunks.append(f"[PAGE {page}]\n{text.strip()}")
            # clear any rendered image left from the last page
        if chunks:
            out = OUT_DIR / f"{asset_id}_raw.txt"
            out.write_text("\n\n".join(chunks), encoding="utf-8")
            stats["ocr_done"] += 1
            stats["pages"] += pages
            print(f"OCR {asset_id}: {pages}/{total_pages} pages [{lang}]")
        else:
            stats["ocr_failed"] += 1
            print(f"OCR_FAIL {asset_id} [{lang}]")

    print(f"EXTRACT_DOCUMENTS_OCR=PASS")
    print(f"SUMMARY={stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
