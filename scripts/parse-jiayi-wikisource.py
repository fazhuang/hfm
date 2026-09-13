#!/usr/bin/env python3
"""P2 篇章段落 — parse Wikisource《针灸甲乙经·宋校本》wikitext into chapters + passages.

Source: zh.wikisource.org 宋校本 (public domain, 皇甫谧 西晋). Raw wikitext is
fetched to ``content-production/corpus/jiayi-wikisource/卷NN.wiki`` (git-ignored).

Outputs two normalized CSVs (tracked):
  content-production/normalized/jiayi-chapters.csv   (卷=level1, 篇=level2)
  content-production/normalized/jiayi-passages.csv   (段 within each 篇)

Parsing rules (documented so the extraction is reproducible):
  * 篇 title lines: ``==...==`` headings OR short plain-text lines ending in
    ``第<num>`` (optionally ``（上）``/``（下）``). The Wikisource markup is
    inconsistent (some 篇 are headings, some are plain text), so both are matched.
  * ``諸穴`` (卷03 section label) and ``鼻鼽息肉`` (卷12 sub-item) are skipped
    as non-篇.
  * ``第五`` (卷02, title missing in source) is kept as an incomplete-title 篇.
  * 段 = blank-line-separated paragraphs; ``{{*|...}}`` collation notes are
    extracted into the ``notes`` column and stripped from content_text.

Usage:
    python scripts/parse-jiayi-wikisource.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
SRC_DIR = REPO_ROOT / "content-production" / "corpus" / "jiayi-wikisource"
OUT_CH = REPO_ROOT / "content-production" / "normalized" / "jiayi-chapters.csv"
OUT_PS = REPO_ROOT / "content-production" / "normalized" / "jiayi-passages.csv"

WORK_ID = "WORK-JIAYI"

# 篇 title suffix: 第 + Chinese number, optional （上）/（下）
_NUM = r"[一二三四五六七八九十百]+"
_TITLE_RE = re.compile(r"第" + _NUM + r"(?:（[上下]）)?$")
# bare "第五" (卷02 incomplete title)
_BARE_TITLE_RE = re.compile(r"^第" + _NUM + r"$")
# inline collation notes: {{*|...}}
_NOTE_RE = re.compile(r"\{\{\*\|(.*?)\}\}", re.S)
# any remaining template {{...}}
_TEMPLATE_RE = re.compile(r"\{\{[^{}]*\}\}", re.S)


def strip_header(text: str) -> str:
    m = re.search(r"\{\{Header.*?\}\}", text, re.S)
    if m:
        return text[: m.start()] + text[m.end():]
    return text


def is_title_line(s: str) -> bool:
    if 2 <= len(s) <= 40 and (_TITLE_RE.search(s) or _BARE_TITLE_RE.search(s)):
        return True
    return False


def heading_text(s: str) -> str | None:
    m = re.match(r"^=+\s*(.+?)\s*=+$", s)
    return m.group(1).strip() if m else None


def extract_notes_and_text(para: str) -> tuple[str, list[str]]:
    notes = [n.strip() for n in _NOTE_RE.findall(para) if n.strip()]
    txt = _NOTE_RE.sub("", para)
    txt = _TEMPLATE_RE.sub("", txt)
    txt = txt.strip()
    return txt, notes


def parse_volume(n: int) -> tuple[list[tuple[str, list[str]]], list[str]]:
    """Return [(篇 title, [段 ...]), ...] and a list of warnings."""
    text = (SRC_DIR / f"卷{n:02d}.wiki").read_text(encoding="utf-8")
    text = strip_header(text)
    lines = text.splitlines()
    warnings: list[str] = []

    pieces: list[tuple[str, list[str]]] = []  # (title, body_lines)
    cur_title: str | None = None
    cur_body: list[str] = []

    def flush() -> None:
        nonlocal cur_title, cur_body
        if cur_title is not None:
            pieces.append((cur_title, cur_body))
        cur_title, cur_body = None, []

    for raw in lines:
        s = raw.strip()
        if not s:
            if cur_title is not None:
                cur_body.append("")  # preserve blank line as 段 separator
            continue
        h = heading_text(s)
        if h is not None:
            t = h.strip()
            if t == "諸穴":
                continue
            if is_title_line(t) or _BARE_TITLE_RE.match(t):
                flush()
                cur_title = t
            else:
                warnings.append(f"卷{n:02d}: heading not 篇-like: {t[:40]}")
                flush()  # unknown heading ends previous 篇; do not start new
            continue
        if is_title_line(s):
            flush()
            cur_title = s
            continue
        if cur_title is not None:
            cur_body.append(raw)
    flush()

    # split body into 段 (blank-line-separated paragraphs)
    result: list[tuple[str, list[str]]] = []
    for title, body in pieces:
        paras = [p.strip() for p in "\n".join(body).split("\n\n") if p.strip()]
        result.append((title, paras))
    return result, warnings


def main() -> int:
    chapters: list[dict[str, object]] = []
    passages: list[dict[str, object]] = []
    all_warnings: list[str] = []

    vol_order = 0
    for n in range(1, 13):
        vol_order += 1
        vol_id = f"CH-JIAYI-V{n:02d}"
        chapters.append({
            "chapter_id": vol_id,
            "work_id": WORK_ID,
            "level": 1,
            "parent_id": "",
            "title": f"卷之{'一二三四五六七八九十十一十二'[n-1]}",
            "order": vol_order,
        })
        pieces, warnings = parse_volume(n)
        all_warnings += warnings
        for i, (title, paras) in enumerate(pieces, start=1):
            pian_id = f"{vol_id}-P{i:02d}"
            chapters.append({
                "chapter_id": pian_id,
                "work_id": WORK_ID,
                "level": 2,
                "parent_id": vol_id,
                "title": title,
                "order": i,
            })
            for j, para in enumerate(paras, start=1):
                content, notes = extract_notes_and_text(para)
                if not content and not notes:
                    continue
                passages.append({
                    "passage_id": f"{pian_id}-D{j:03d}",
                    "chapter_id": pian_id,
                    "content_text": content,
                    "notes": " | ".join(notes),
                    "order": j,
                })

    # write chapters
    with OUT_CH.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["chapter_id", "work_id", "level", "parent_id", "title", "order"])
        w.writeheader()
        w.writerows(chapters)
    with OUT_PS.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["passage_id", "chapter_id", "content_text", "notes", "order"])
        w.writeheader()
        w.writerows(passages)

    pian = [c for c in chapters if c["level"] == 2]
    print(f"PARSE_JIAYI=PASS")
    print(f"卷 chapters: {vol_order}")
    print(f"篇 chapters: {len(pian)}")
    print(f"passages: {len(passages)}")
    print(f"warnings: {len(all_warnings)}")
    for w in all_warnings:
        print(f"  WARN {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
