#!/usr/bin/env python3
"""HFM P2 redaction pipeline — stages 1–2: redact and register a derivative.

Produces a redacted public derivative for a P2 media asset (policy
``HFM-ASSET-PRESENTATION-POLICY.md`` §4.1) and registers it in
``media_assets`` via ``MediaService.create_derivative`` — original/derivative
linkage plus a deterministic redaction token, both hash-bound.

Three subcommands:

  --detect         Propose redaction regions for the P2 assets in a
                   classification sheet: extract text (PDF text layer, else
                   tesseract OCR) and match personal-information patterns.
                   Writes a DRAFT spec for a human to review. Never writes
                   media, never touches the database.

  --render-pages   Render each P2 page to PNG with a coordinate grid in PDF
                   points, for a person to read the sensitive regions off.
                   This is the manual half of the workflow (see the limitation
                   note below).

  --apply          Take a REVIEWED spec and produce the derivatives.

Redaction method by format:

  .pdf    true redaction (PyMuPDF ``apply_redactions``): the covered glyphs and
          image pixels are removed from the file, not merely painted over —
          paint over a text layer is recoverable, which on P2 material is no
          redaction at all.
  .docx   personal-information runs blanked in the OOXML text parts. Fails if
          the value spans several Word runs and cannot be fully blanked.
  .jpg    opaque boxes over reviewed regions; re-encoded without EXIF.
  .doc    NO PATH. Legacy binary Word has no safe in-place editor here, so the
          run refuses it rather than silently passing the original through.

Why the spec is a separate, signed artifact: the sensitive region of a
certificate scan cannot be found reliably by machine. Detection proposes; a
human confirms. The spec therefore binds ``source_sha256`` — if the source
bytes change, the confirmed regions no longer describe the file and the run
fails rather than redacting the wrong thing.

Fail-closed rules:
  - the spec must bind ``source_sha256`` and it must match the registered row;
  - a derivative key must live under the derivative root, differ from the
    source key, and must not already exist as a file or a row;
  - the derivative must differ in bytes from its source;
  - **verified redaction**, in two assurance classes: regions over vector text
    are checked exactly (SURVIVOR tokens and PII patterns must be absent from
    the derivative's text layer); regions over a scan are checked on rendered
    pixels (the source region must not already be black, and the derivative
    region must be fully covered by the fill). A derivative that fails either
    check is deleted and never registered;
  - nothing is written to the client source tree — ``hfmzl/`` is untouched.

Known limitation: automatic region *detection* does not work on the client's
scanned certificates. Tesseract with ``chi_sim`` returns mostly garbage on
them, so no sensitive field can be located automatically, and the same
weakness is why OCR is not used as a verification probe either. Those 58
assets need regions specified by a person looking at the page.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python redact-media-derivative.py --detect \
        --classification content-production/07-review/heritage-evidence-classification.csv \
        --emit-spec content-production/07-review/redaction-specs/heritage-evidence.spec.json
    # review + sign the spec, then:
    python redact-media-derivative.py --apply \
        --spec content-production/07-review/redaction-specs/heritage-evidence.spec.json \
        --env-file ~/.hfm/secrets/prod.env
    # add --commit to write; default is --dry-run (report + rollback)

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "apps" / "backend"

#: Object keys of derivatives live under this prefix (distinct from the client's
#: ``非遗佐证/`` tree so a derivative is never mistaken for a delivered original).
DERIVATIVE_PREFIX = "非遗佐证-脱敏/"

#: Redaction rule id recorded on the derivative's deterministic token.
REDACTION_RULE = "heritage-p2-redact-v1"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_module("validate_production_env", _SCRIPT_DIR / "validate-production-env.py")

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.core.config import DERIVATIVE_ROOT, MEDIA_ROOT  # noqa: E402
from hfm.phase2.media.models import MediaAsset  # noqa: E402
from hfm.phase2.media.service import MediaService, compute_sha256  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

#: Detection patterns — deliberately PERMISSIVE. A hit is a *candidate* region
#: for a human to confirm, so a false positive costs one review note while a
#: false negative leaks personal data. ``mobile_cn`` matches 9–10 digits, not
#: the full 11, because a roster cell wraps its last digit onto the next line
#: ("1529403668" / "2") and the 11-digit form matches no single word.
DETECT_PATTERNS: dict[str, str] = {
    "mobile_cn": r"1[3-9]\d{7,9}",
    "landline_cn": r"0\d{2,3}-?\d{7,8}",
    "id_card_cn": r"\d{15,17}[\dXx]",
    "bank_account": r"\d{12,19}",
    "certificate_no": r"(?:证书编号|证号|编号|文号|字第)\s*[:：]?\s*[A-Za-z0-9〔〕（）()\-—]{2,}",
    "signature_block": r"(?:签\s*字|签\s*章|本人签名)",
}

#: Verification patterns — deliberately STRICT, applied to the derivative's
#: text with all whitespace squeezed out. Anything still matching here means
#: the redaction did not take, so the run fails and the derivative is dropped.
VERIFY_PATTERNS: dict[str, str] = {
    "mobile_cn": r"1[3-9]\d{9}",
    "landline_cn": r"0\d{2,3}-?\d{7,8}",
    "id_card_cn": r"\d{17}[\dXx]",
    "bank_account": r"\d{16,19}",
}


@dataclass(frozen=True)
class Region:
    """One redaction rectangle in PDF points, absolute on the page."""

    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    basis: str


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


#: A page whose text layer holds fewer than this many characters is treated as
#: an image. Scanner apps stamp a short watermark ("扫描全能王 创建", 8 chars)
#: onto an otherwise pure-image page, and a naive "text layer is non-empty"
#: test lets that watermark suppress OCR entirely — which would silently
#: propose no regions for 58 of the 60 heritage PDFs.
MIN_TEXT_LAYER_CHARS = 40


def _text_words(path: Path) -> list[tuple[int, tuple[float, float, float, float], str]]:
    """Extract words with page + bbox, via the text layer or OCR."""
    import pymupdf

    out: list[tuple[int, tuple[float, float, float, float], str]] = []
    document = pymupdf.open(path)
    try:
        for index, page in enumerate(document):
            page_no = index + 1
            words = page.get_text("words")
            substantive = sum(len(str(w[4]).strip()) for w in words) >= MIN_TEXT_LAYER_CHARS
            if substantive:
                for x0, y0, x1, y1, text, *_ in words:
                    out.append((page_no, (x0, y0, x1, y1), str(text)))
                continue
            out.extend(_ocr_words(page, page_no))
    finally:
        document.close()
    return out


def _ocr_words(page: Any, page_no: int) -> list[tuple[int, tuple[float, float, float, float], str]]:
    """OCR one page via tesseract TSV; bboxes are converted to PDF points.

    A page with no text layer is an image of a document, so the only way to
    find its fields is to read the pixels.
    """
    scale = 300 / 72  # render at 300 dpi for OCR, report in PDF points
    pixmap = page.get_pixmap(dpi=300)
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "page.png"
        pixmap.save(png)
        result = subprocess.run(
            ["tesseract", str(png), "stdout", "-l", "chi_sim+eng", "tsv"],
            capture_output=True,
            text=True,
            check=False,
        )
    out: list[tuple[int, tuple[float, float, float, float], str]] = []
    for line in result.stdout.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 12:
            continue
        try:
            left = float(parts[6])
            top = float(parts[7])
            width = float(parts[8])
            height = float(parts[9])
        except ValueError:
            continue
        text = parts[11].strip()
        if not text:
            continue
        box = (left / scale, top / scale, (left + width) / scale, (top + height) / scale)
        out.append((page_no, box, text))
    return out


def _match_pii(text: str) -> list[str]:
    return [name for name, pattern in DETECT_PATTERNS.items() if re.search(pattern, text)]


def detect_regions(path: Path) -> list[Region]:
    """Propose redaction regions for one PDF from its extracted text.

    A roster column is proposed as one tall region when three or more sensitive
    tokens line up vertically — a phone column often wraps its last digit onto
    the next text line, so per-token boxes would miss it.
    """
    words = _text_words(path)
    hits = [(page, box, text, _match_pii(text)) for page, box, text in words]
    hits = [h for h in hits if h[3]]

    regions: list[Region] = []
    by_page: dict[int, list[tuple[tuple[float, float, float, float], str, list[str]]]] = {}
    for page, box, text, matched in hits:
        by_page.setdefault(page, []).append((box, text, matched))

    for page, items in sorted(by_page.items()):
        # Column clusters: tokens whose x-centres sit within 6pt of each other.
        columns: list[list[tuple[tuple[float, float, float, float], str, list[str]]]] = []
        for item in sorted(items, key=lambda i: i[0][0]):
            centre = (item[0][0] + item[0][2]) / 2
            for column in columns:
                existing = (column[0][0][0] + column[0][0][2]) / 2
                if abs(centre - existing) <= 6:
                    column.append(item)
                    break
            else:
                columns.append([item])

        for column in columns:
            if len(column) >= 3:
                x0 = min(i[0][0] for i in column)
                y0 = min(i[0][1] for i in column)
                x1 = max(i[0][2] for i in column)
                y1 = max(i[0][3] for i in column)
                kinds = sorted({k for i in column for k in i[2]})
                regions.append(
                    Region(page, x0 - 4, y0 - 4, x1 + 4, y1 + 4, f"列簇 {kinds} ×{len(column)}")
                )
            else:
                for box, _text, matched in column:
                    regions.append(
                        Region(page, box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4, f"单点 {matched}")
                    )
    return regions


def _apply_regions(source: Path, target: Path, regions: list[Region]) -> None:
    """True redaction: remove the covered text and image pixels, then save."""
    import pymupdf

    document = pymupdf.open(source)
    try:
        pages = {r.page for r in regions}
        for page_no in pages:
            page = document[page_no - 1]
            for region in regions:
                if region.page != page_no:
                    continue
                page.add_redact_annot(
                    pymupdf.Rect(region.x0, region.y0, region.x1, region.y1), fill=(0, 0, 0)
                )
            page.apply_redactions(
                images=pymupdf.PDF_REDACT_IMAGE_PIXELS,
                graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
                text=pymupdf.PDF_REDACT_TEXT_REMOVE,
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        document.save(target, garbage=4, deflate=True)
    finally:
        document.close()


def _images_overlapping(source: Any, page_no: int, region: Region) -> bool:
    """Does any image XObject on this page overlap the region?

    Overlap decides which verification is even applicable: a region over pure
    vector text can be verified exactly from the text layer, while a region
    over a scan has no text layer to consult and needs a pixel probe.
    """
    import pymupdf

    page = source[page_no - 1]
    clip = pymupdf.Rect(region.x0, region.y0, region.x1, region.y1)
    for info in page.get_images(full=True):
        for rect in page.get_image_rects(info[0]):
            if clip.intersects(rect):
                return True
    return False


def _fill_fraction(path: Path, region: Region, dpi: int = 150) -> float:
    """Fraction of a region's rendered pixels that are the black redaction fill.

    A deterministic alternative to an OCR probe. Tesseract misreads small table
    digits in these scans — on the 平凉市名中医 certificate it returns mostly
    garbage — so an OCR-based "did the value survive?" probe would report a
    clean result on documents it cannot actually read. That is false assurance.
    Counting fill pixels is exact and does not depend on reading anything.
    """
    import pymupdf

    document = pymupdf.open(path)
    try:
        page = document[region.page - 1]
        clip = pymupdf.Rect(region.x0, region.y0, region.x1, region.y1)
        pixmap = page.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csGRAY)
        samples = pixmap.samples
        if not samples:
            return 0.0
        dark = sum(1 for value in samples if value <= 32)
        return dark / len(samples)
    finally:
        document.close()


def verify_redaction(derivative: Path, original: Path, regions: list[Region]) -> tuple[list[str], list[str]]:
    """Prove the redaction took. Returns ``(errors, notes)``.

    Two independent checks, and it matters which one applies:

    *Text layer* (exact). Every token that sat inside a reviewed region in the
    source is looked up in the derivative. This is complete for vector/typed
    content — the glyphs are simply gone or they are not.

    *Pixels* (probed). A region over a scan has no text layer, so the only
    evidence is the rendered pixels themselves. Two conditions must hold, and
    the assurance is explicitly weaker than the text-layer check:

      1. the source region is **not** uniformly black — otherwise the redaction
         covered nothing, and a "clean" derivative would be meaningless;
      2. the derivative region **is** uniformly black — the fill actually landed.

    PyMuPDF's ``PDF_REDACT_IMAGE_PIXELS`` blanks the covered pixels in the
    image object itself rather than layering paint over them; the uniformity
    check confirms the fill, and the removal is what ``apply_redactions`` does.
    That chain is weaker than "the glyph is simply gone", so it is reported as
    a note rather than silently equated with the exact check.
    """
    import pymupdf

    errors: list[str] = []
    notes: list[str] = []

    # ---- text layer: exact, and complete for anything with a text layer.
    survivor_checks: list[str] = []
    source = pymupdf.open(original)
    try:
        for region in regions:
            page = source[region.page - 1]
            clip = pymupdf.Rect(region.x0, region.y0, region.x1, region.y1)
            for token in page.get_text("words"):
                x0, y0, x1, y1, text = token[0], token[1], token[2], token[3], str(token[4])
                if clip.intersects(pymupdf.Rect(x0, y0, x1, y1)) and len(text.strip()) >= 4:
                    survivor_checks.append(text.strip())
    finally:
        source.close()

    derivative_text = " ".join(text for _page, _box, text in _text_words(derivative))
    squeezed = re.sub(r"\s+", "", derivative_text)

    for name, pattern in VERIFY_PATTERNS.items():
        if re.search(pattern, squeezed):
            errors.append(f"derivative still matches {name} in its text layer")

    for token in survivor_checks:
        compact = re.sub(r"\s+", "", token)
        if len(compact) >= 4 and compact in squeezed:
            errors.append(f"redacted token survives in the derivative text layer: {token!r}")

    # ---- pixels: only for regions that actually sit over an image.
    source = pymupdf.open(original)
    try:
        scanned = [r for r in regions if _images_overlapping(source, r.page, r)]
    finally:
        source.close()

    if not scanned:
        notes.append("所有区域均为矢量文本层，文本层精确校验即为完整证据")
        return errors, notes

    for region in scanned:
        where = (
            f"p{region.page} ({region.x0:.0f},{region.y0:.0f})-"
            f"({region.x1:.0f},{region.y1:.0f})"
        )
        before = _fill_fraction(original, region)
        after = _fill_fraction(derivative, region)
        if before >= 0.95:
            errors.append(
                f"{where}: 原件该区域本就是纯黑 —— 该区域未覆盖任何内容，无法证明脱敏有效"
            )
            continue
        if after < 0.95:
            errors.append(
                f"{where}: 脱敏件该区域黑色填充仅占 {after:.0%} —— 遮挡未完整覆盖该区域"
            )
    notes.append(
        f"扫描图像区域 {len(scanned)} 处：以渲染像素校验（弱于文本层精确校验 —— "
        "扫描件无文字层，OCR 探针在本批证书上无法标定，故不作依据）"
    )
    return errors, notes



# ------------------------------------------------- non-PDF redaction


#: Parts of an OOXML package that can carry document text.
_DOCX_TEXT_PARTS = ("word/document.xml", "word/header", "word/footer", "word/footnotes.xml")


def _redact_docx(source: Path, target: Path, _regions: list[Region]) -> int:
    """Blank personal-information runs inside a .docx package.

    Word splits a visible string across runs whenever formatting changes, so a
    number is often not contained in any single ``<w:t>``. This replaces within
    runs and returns how many it changed; the caller's verification then
    re-reads the whole paragraph text and fails if a pattern survives, which is
    what catches the cross-run case. Refusing to emit such a file is the right
    outcome — a half-redacted press release is worse than an unprocessed one.
    """
    import zipfile

    replacements = 0
    with zipfile.ZipFile(source) as zin:
        names = zin.namelist()
        payload = {name: zin.read(name) for name in names}

    for name in names:
        if not any(name.startswith(part) for part in _DOCX_TEXT_PARTS):
            continue
        if not name.endswith(".xml"):
            continue
        xml = payload[name].decode("utf-8")

        def blank(match: re.Match[str]) -> str:
            nonlocal replacements
            inner = match.group(2)
            for pattern in DETECT_PATTERNS.values():
                new_inner, count = re.subn(pattern, lambda m: "█" * len(m.group(0)), inner)
                if count:
                    replacements += count
                inner = new_inner
            return f"{match.group(1)}{inner}{match.group(3)}"

        payload[name] = re.sub(r"(<w:t[^>]*>)([^<]*)(</w:t>)", blank, xml).encode("utf-8")

    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            zout.writestr(name, payload[name])
    return replacements


def _redact_image(source: Path, target: Path, regions: list[Region]) -> None:
    """Paint opaque boxes over an image.

    Fractions of the image box (0..1) rather than pixels, so a spec stays valid
    if the same page is re-rendered at a different resolution. The source is
    re-encoded rather than saved in place, so no original pixels survive in a
    trailing scan-line or an EXIF thumbnail.
    """
    from PIL import Image, ImageDraw

    with Image.open(source) as opened:
        image = opened.convert("RGB")
        draw = ImageDraw.Draw(image)
        for region in regions:
            width, height = image.size
            draw.rectangle(
                [
                    region.x0 * width,
                    region.y0 * height,
                    region.x1 * width,
                    region.y1 * height,
                ],
                fill=(0, 0, 0),
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, format="JPEG", quality=95, exif=b"")


def verify_docx(derivative: Path) -> tuple[list[str], list[str]]:
    """Re-read every paragraph of the redacted package and look for survivors."""
    import zipfile

    errors: list[str] = []
    parts: list[str] = []
    with zipfile.ZipFile(derivative) as zf:
        for name in zf.namelist():
            if any(name.startswith(part) for part in _DOCX_TEXT_PARTS) and name.endswith(".xml"):
                xml = zf.read(name).decode("utf-8", "replace")
                parts.append("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)))
    squeezed = re.sub(r"\s+", "", "".join(parts))
    for name, pattern in VERIFY_PATTERNS.items():
        if re.search(pattern, squeezed):
            errors.append(
                f"derivative still matches {name} — the value likely spans multiple "
                f"Word runs and was not fully blanked; handle this file manually"
            )
    return errors, ["docx：逐段重读校验"]


def verify_image(derivative: Path, source: Path, regions: list[Region]) -> tuple[list[str], list[str]]:
    """Every reviewed region must be fully black in the derivative."""
    from PIL import Image

    errors: list[str] = []
    with Image.open(derivative) as opened:
        image = opened.convert("RGB")
        width, height = image.size
        for region in regions:
            box = (
                int(region.x0 * width),
                int(region.y0 * height),
                int(region.x1 * width),
                int(region.y1 * height),
            )
            crop = image.crop(box)
            pixels = list(crop.getdata())
            if not pixels:
                errors.append(f"区域 {box} 为空 — 无法证明遮挡")
                continue
            dark = sum(1 for p in pixels if max(p) <= 32)
            if dark / len(pixels) < 0.95:
                errors.append(f"区域 {box} 黑色填充仅占 {dark / len(pixels):.0%} — 遮挡未完整覆盖")
    return errors, ["图片：渲染像素填充校验（弱于文本层精确校验）"]


#: Formats whose redaction is driven by reviewed regions (as opposed to whole-
#: document text matching, where the pattern set is the contract).
_REGION_FORMATS = frozenset({".pdf", ".jpg", ".jpeg"})

#: Formats redacted by matching the pattern set across the document text.
_TEXT_PATTERN_FORMATS = frozenset({".docx"})

#: Format -> redactor. A format absent here has no redaction path and the run
#: refuses it rather than passing the original through: legacy .doc has no
#: safe in-place editor available, so it must be converted first.
_REDACTORS: dict[str, Any] = {
    ".pdf": _apply_regions,
    ".jpg": _redact_image,
    ".jpeg": _redact_image,
    ".docx": _redact_docx,
}

#: Format -> verifier. Docx ignores the region list (whole-document patterns).
_VERIFIERS: dict[str, Any] = {
    ".pdf": verify_redaction,
    ".jpg": verify_image,
    ".jpeg": verify_image,
    ".docx": lambda derivative, _source, _regions: verify_docx(derivative),
}


# ------------------------------------------------------------------ spec I/O


def load_spec(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"cannot read redaction spec: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("assets"), list) or not raw["assets"]:
        raise ValueError("redaction spec requires a non-empty 'assets' list")
    for index, asset in enumerate(raw["assets"]):
        where = f"assets[{index}]"
        for field in ("object_key", "derivative_object_key", "source_sha256"):
            if not asset.get(field):
                raise ValueError(f"{where}.{field} is required")
        # Region-driven formats must state their regions; text-pattern formats
        # (docx) derive theirs from the pattern set, so 'pages' is optional.
        if Path(str(asset["object_key"])).suffix.lower() in _REGION_FORMATS and not asset.get(
            "pages"
        ):
            raise ValueError(
                f"{where}.pages is required for {Path(str(asset['object_key'])).suffix} "
                f"(region-driven redaction)"
            )
        if not str(asset["derivative_object_key"]).startswith(DERIVATIVE_PREFIX):
            raise ValueError(
                f"{where}.derivative_object_key must start with {DERIVATIVE_PREFIX!r}"
            )
        if asset["derivative_object_key"] == asset["object_key"]:
            raise ValueError(f"{where} derivative key must differ from the source key")
        if not asset.get("reviewed_by"):
            raise ValueError(
                f"{where}.reviewed_by is empty — a redaction spec must be reviewed by a "
                "named person before it can be applied"
            )
    return raw


def spec_regions(asset: dict[str, Any]) -> list[Region]:
    regions: list[Region] = []
    for page in asset.get("pages", []):
        page_no = int(page["page"])
        for region in page["regions"]:
            regions.append(
                Region(
                    page=page_no,
                    x0=float(region["x0"]),
                    y0=float(region["y0"]),
                    x1=float(region["x1"]),
                    y1=float(region["y1"]),
                    basis=str(region.get("basis", "")),
                )
            )
    return regions


# ------------------------------------------------------------------ commands


def _detect(args: argparse.Namespace) -> int:
    import csv

    rows = list(csv.DictReader(args.classification.open(encoding="utf-8")))
    targets = [r for r in rows if r["privacy_class"] == "P2"]
    print(f"CLASSIFICATION={args.classification}")
    print(f"P2_ASSETS={len(targets)}")

    assets: list[dict[str, Any]] = []
    for row in targets:
        object_key = row["object_key"]
        source = Path(MEDIA_ROOT) / object_key
        if not source.is_file():
            print(f"SKIP (source missing) {object_key}")
            continue
        if source.suffix.lower() != ".pdf":
            print(f"NEEDS_MANUAL_REVIEW (not a PDF) {object_key}")
            continue
        regions = detect_regions(source)
        print(f"PROPOSED {len(regions):3d} regions  {object_key}")
        for region in regions:
            print(
                f"    p{region.page} ({region.x0:.0f},{region.y0:.0f})-"
                f"({region.x1:.0f},{region.y1:.0f}) {region.basis}"
            )
        assets.append(
            {
                "object_key": object_key,
                "derivative_object_key": DERIVATIVE_PREFIX + object_key[len("非遗佐证/") :],
                "source_sha256": sha256_of(source),
                "reviewed_by": "",
                "reviewed_on": "",
                "pages": _regions_to_spec_pages(regions),
            }
        )

    spec = {
        "version": 1,
        "rule": REDACTION_RULE,
        "status": "DRAFT — 待人工逐条复核并签署 reviewed_by 后方可 --apply",
        "assets": assets,
    }
    args.emit_spec.parent.mkdir(parents=True, exist_ok=True)
    args.emit_spec.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"SPEC_WRITTEN {args.emit_spec}")
    print(f"DETECTED_ASSETS={len(assets)}")
    print("RESULT=PASS")
    return 0


def _regions_to_spec_pages(regions: list[Region]) -> list[dict[str, Any]]:
    by_page: dict[int, list[dict[str, Any]]] = {}
    for region in regions:
        by_page.setdefault(region.page, []).append(
            {
                "x0": round(region.x0, 2),
                "y0": round(region.y0, 2),
                "x1": round(region.x1, 2),
                "y1": round(region.y1, 2),
                "basis": region.basis,
            }
        )
    return [{"page": page, "regions": items} for page, items in sorted(by_page.items())]


async def _apply(args: argparse.Namespace, env: dict[str, str]) -> int:
    try:
        spec = load_spec(args.spec)
    except ValueError as exc:
        print(f"SPEC=FAIL ({exc})")
        return 1

    engine = create_async_engine(env["HFM_DATABASE_URL"])
    failures = 0
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            service = MediaService(session)
            try:
                for asset_spec in spec["assets"]:
                    object_key = asset_spec["object_key"]
                    derivative_key = asset_spec["derivative_object_key"]
                    asset = (
                        await session.execute(
                            select(MediaAsset).where(MediaAsset.object_key == object_key)
                        )
                    ).scalar_one_or_none()
                    if asset is None:
                        print(f"FAIL {object_key}: not registered in media_assets")
                        failures += 1
                        continue
                    if str(asset.sha256) != asset_spec["source_sha256"]:
                        print(
                            f"FAIL {object_key}: source bytes changed since the spec was "
                            f"reviewed (registered {str(asset.sha256)[:12]}…, "
                            f"spec {asset_spec['source_sha256'][:12]}…)"
                        )
                        failures += 1
                        continue
                    if str(asset.privacy_class) != "P2":
                        print(f"FAIL {object_key}: registered {asset.privacy_class}, not P2")
                        failures += 1
                        continue

                    source = Path(MEDIA_ROOT) / object_key
                    target = Path(DERIVATIVE_ROOT) / derivative_key
                    if target.exists():
                        print(f"FAIL {derivative_key}: derivative file already exists")
                        failures += 1
                        continue
                    existing = await service.get(derivative_key)
                    if existing is not None:
                        print(f"FAIL {derivative_key}: derivative already registered")
                        failures += 1
                        continue

                    suffix = source.suffix.lower()
                    if suffix not in _REDACTORS:
                        print(
                            f"FAIL {object_key}: {suffix or '(no extension)'} has no redaction "
                            f"path — convert it to a supported format or handle it manually"
                        )
                        failures += 1
                        continue

                    regions = spec_regions(asset_spec)
                    if suffix in _REGION_FORMATS and not regions:
                        print(f"FAIL {object_key}: spec carries no regions")
                        failures += 1
                        continue

                    if args.dry_run:
                        scratch = Path(tempfile.mkdtemp()) / target.name
                    else:
                        scratch = target
                    replaced = _REDACTORS[suffix](source, scratch, regions)
                    # A text-pattern format reports how many strings it blanked.
                    # Zero means the file matched nothing — registering it would
                    # create a "redacted derivative" that is simply a re-encoded
                    # original, which is exactly the false assurance this pipeline
                    # exists to prevent.
                    if suffix in _TEXT_PATTERN_FORMATS and not replaced:
                        print(
                            f"FAIL {object_key}: no personal-information pattern matched — "
                            f"nothing was redacted, refusing to register a derivative"
                        )
                        failures += 1
                        scratch.unlink(missing_ok=True)
                        continue

                    problems, notes = _VERIFIERS[suffix](scratch, source, regions)
                    for note in notes:
                        print(f"  NOTE {object_key}: {note}")
                    if problems:
                        for problem in problems:
                            print(f"FAIL {object_key}: {problem}")
                        failures += 1
                        scratch.unlink(missing_ok=True)
                        continue

                    digest = sha256_of(scratch)
                    if digest == asset_spec["source_sha256"]:
                        print(f"FAIL {object_key}: derivative bytes equal the source")
                        failures += 1
                        scratch.unlink(missing_ok=True)
                        continue

                    await service.create_derivative(
                        original_object_key=object_key,
                        object_key=derivative_key,
                        mime_type=str(asset.mime_type),
                        byte_size=scratch.stat().st_size,
                        sha256=digest,
                        redaction_rule=spec["rule"],
                    )
                    print(
                        f"OK {object_key} -> {derivative_key} "
                        f"({len(regions)} regions, {scratch.stat().st_size} bytes, "
                        f"reviewed_by={asset_spec['reviewed_by']})"
                    )
                    if args.dry_run:
                        scratch.unlink(missing_ok=True)

                if args.dry_run:
                    await session.rollback()
                    print("DRY_RUN=ROLLED_BACK (no commit)")
                else:
                    await session.commit()
            except BaseException:
                await session.rollback()
                raise
    finally:
        await engine.dispose()

    print(f"FAILURES={failures}")
    if failures:
        print("RESULT=FAIL")
        return 1
    print("RESULT=PASS")
    return 0


def _render_pages(args: argparse.Namespace) -> int:
    """Render each P2 page to PNG with a labelled coordinate grid.

    This is the human half of the workflow. Automatic detection cannot read the
    client's scanned certificates (tesseract returns garbage on them), so a
    person has to look at the page and say where the certificate number and the
    signature sit. The grid is drawn in PDF points — the same units the spec
    takes — so the numbers can be read straight off the image and typed into
    the spec without any conversion.
    """
    import csv

    import pymupdf

    rows = list(csv.DictReader(args.classification.open(encoding="utf-8")))
    targets = [r for r in rows if r["privacy_class"] == "P2"]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rendered = 0
    for row in targets:
        object_key = row["object_key"]
        source = Path(MEDIA_ROOT) / object_key
        if not source.is_file() or source.suffix.lower() != ".pdf":
            continue
        slug = re.sub(r"[^\w一-鿿]+", "_", object_key[len("非遗佐证/") :]).strip("_")
        stem = slug[:80]
        document = pymupdf.open(source)
        try:
            for index, page in enumerate(document):
                rect = page.rect
                step = 50
                for x in range(0, int(rect.width) + 1, step):
                    page.draw_line(
                        pymupdf.Point(x, 0), pymupdf.Point(x, rect.height), color=(1, 0, 0), width=0.3
                    )
                    page.insert_text(
                        pymupdf.Point(x + 1, 9), str(x), fontsize=5, color=(1, 0, 0)
                    )
                for y in range(0, int(rect.height) + 1, step):
                    page.draw_line(
                        pymupdf.Point(0, y), pymupdf.Point(rect.width, y), color=(1, 0, 0), width=0.3
                    )
                    page.insert_text(pymupdf.Point(1, y + 8), str(y), fontsize=5, color=(1, 0, 0))
                pixmap = page.get_pixmap(dpi=args.render_dpi)
                out = args.out_dir / f"{stem}__p{index + 1}.png"
                pixmap.save(out)
                rendered += 1
                print(f"RENDERED {out}  (page box {rect.width:.0f} x {rect.height:.0f} pt)")
        finally:
            document.close()
    print(f"OUT_DIR={args.out_dir}")
    print(f"PAGES_RENDERED={rendered}")
    print("NEXT: 逐张看图，记下敏感字段的 x0,y0,x1,y1（PDF 点，图上红字即坐标），")
    print("      写入 spec 的 pages[].regions，填好 reviewed_by 后再 --apply")
    print("RESULT=PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--detect", action="store_true", help="propose redaction regions")
    mode.add_argument("--apply", action="store_true", help="apply a reviewed spec")
    mode.add_argument(
        "--render-pages",
        action="store_true",
        help="render P2 pages with a coordinate grid for manual region marking",
    )
    parser.add_argument("--classification", type=Path, default=None)
    parser.add_argument("--emit-spec", type=Path, default=None)
    parser.add_argument("--spec", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--render-dpi", type=int, default=150)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--commit", dest="dry_run", action="store_false")
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--allow-sqlite", action="store_true")
    args = parser.parse_args(argv)

    if args.render_pages:
        if args.classification is None or args.out_dir is None:
            print("USAGE=FAIL (--render-pages requires --classification and --out-dir)")
            return 2
        if not args.classification.is_file():
            print(f"CLASSIFICATION=FAIL (not found: {args.classification})")
            return 1
        return _render_pages(args)

    if args.detect:
        if args.classification is None or args.emit_spec is None:
            print("USAGE=FAIL (--detect requires --classification and --emit-spec)")
            return 2
        if not args.classification.is_file():
            print(f"CLASSIFICATION=FAIL (not found: {args.classification})")
            return 1
        return _detect(args)

    if args.spec is None:
        print("USAGE=FAIL (--apply requires --spec)")
        return 2
    if not args.spec.is_file():
        print(f"SPEC=FAIL (not found: {args.spec})")
        return 1

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        env.update(validator.parse_env_file(args.env_file))

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(env, environment=environment, allow_sqlite=args.allow_sqlite)
    if errors:
        for error in errors:
            print(f"ENV=FAIL ({error})")
        return 1
    if not env.get("HFM_DATABASE_URL"):
        print("ENV=FAIL (HFM_DATABASE_URL missing)")
        return 1
    if shutil.which("tesseract") is None:
        print("ENV=FAIL (tesseract not found — verification OCR cannot run)")
        return 1

    print(f"SPEC={args.spec}")
    return asyncio.run(_apply(args, env))


if __name__ == "__main__":
    raise SystemExit(main())
