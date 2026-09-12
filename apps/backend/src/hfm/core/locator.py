"""Structured text locator value object (CD-0 — Foundation).

HFM-native (NEW). Extends the unstructured HFB `SourceRef.page_location`
string into a structured locator per HFM-CORE-DOMAIN-SCOPE §6.2 and
HFM-EVIDENCE-LINEAGE-CONTRACT §3. Serializes to JSON for persistence.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Locator(BaseModel):
    """Structured locator for a text unit or source reference.

    All fields optional: a locator may point at an entity level
    (work/edition/version/chapter/passage ids) and/or a physical position
    (volume/section/page/line).
    """

    work_id: str | None = None
    edition_id: str | None = None
    version_id: str | None = None
    chapter_id: str | None = None
    passage_id: str | None = None
    volume: str | None = Field(default=None, description="卷")
    section: str | None = Field(default=None, description="篇/部")
    page: str | None = Field(default=None, description="页/栏")
    line: str | None = Field(default=None, description="行")

    def to_locator_string(self) -> str:
        """Render a human-readable locator string (best-effort)."""
        parts = [
            f"work:{self.work_id}" if self.work_id else None,
            f"edition:{self.edition_id}" if self.edition_id else None,
            f"version:{self.version_id}" if self.version_id else None,
            f"chapter:{self.chapter_id}" if self.chapter_id else None,
            f"passage:{self.passage_id}" if self.passage_id else None,
        ]
        physical = ".".join(p for p in (self.volume, self.section, self.page, self.line) if p)
        if physical:
            parts.append(f"loc:{physical}")
        rendered = ",".join(p for p in parts if p)
        return rendered or "unlocated"

    def is_empty(self) -> bool:
        """True when no entity anchor and no physical position is set."""
        return not any(
            (
                self.work_id,
                self.edition_id,
                self.version_id,
                self.chapter_id,
                self.passage_id,
                self.volume,
                self.section,
                self.page,
                self.line,
            )
        )

    def model_dump_json_compact(self) -> str:
        return self.model_dump_json(exclude_none=True)

    @staticmethod
    def from_mapping(data: dict[str, Any] | None) -> Locator:
        """Build a Locator from a persisted JSON mapping (missing keys → None)."""
        return Locator(**data) if data else Locator()

    @staticmethod
    def from_locator_string(value: str) -> Locator:
        """Parse a locator string rendered by ``to_locator_string()``.

        Entity anchors (work/edition/version/chapter/passage) are parsed
        strictly and carry the resolution semantics; the physical
        ``loc:v.s.p.l`` segment is parsed right-anchored (finest segment
        last) for display only and is never used for anchoring. Malformed
        or anchor-less strings fail closed (P1-07 reader, E-07).
        """
        if not value or value.strip() == "unlocated":
            raise ValueError("empty locator")
        entity_keys = {
            "work": "work_id",
            "edition": "edition_id",
            "version": "version_id",
            "chapter": "chapter_id",
            "passage": "passage_id",
        }
        data: dict[str, Any] = {}
        physical: list[str] = []
        for part in value.split(","):
            part = part.strip()
            if not part:
                raise ValueError(f"malformed locator part: {part!r}")
            key, _, raw = part.partition(":")
            raw = raw.strip()
            if key == "loc":
                physical = [seg for seg in raw.split(".") if seg]
                continue
            if key not in entity_keys:
                raise ValueError(f"unknown locator key: {key}")
            if not raw:
                raise ValueError(f"empty locator value: {key}")
            data[entity_keys[key]] = raw
        # Right-anchored physical mapping: ...volume.section.page.line.
        # The canonical system locators (section.line) round-trip exactly;
        # partial physical segments stay display-only metadata.
        if physical:
            segments = physical[-4:]
            fields = ("volume", "section", "page", "line")
            for field, seg in zip(fields[-len(segments) :], segments, strict=True):
                data[field] = seg
        locator = Locator(**data)
        if locator.is_empty():
            raise ValueError("locator has no anchor")
        return locator
