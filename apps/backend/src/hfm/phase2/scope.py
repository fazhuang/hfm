"""Phase-2 scope taxonomy verification (P2-00 contract verifier).

Parses the frozen HFM-PHASE2-SCOPE-REGISTER-v1.md and verifies the scope
taxonomy invariant: every governed scope row has exactly one classification
(IN / DEPENDENCY_ONLY / DEFERRED / REJECTED), no duplicate scope IDs, and no
illegal classification.

Frozen finding F-01 semantics: the register contains 15 P2-C* requirement
rows plus the carried P2-CLINICAL rejected guard, i.e. 16 classified rows in
the complete register. Verification is semantic (each row classified exactly
once), never a hardcoded count string.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: Frozen classification vocabulary (HFM-PHASE2-SCOPE-REGISTER-v1.md).
IN = "IN"
DEPENDENCY_ONLY = "DEPENDENCY_ONLY"
DEFERRED = "DEFERRED"
REJECTED = "REJECTED"
CLASSIFICATIONS: tuple[str, ...] = (IN, DEPENDENCY_ONLY, DEFERRED, REJECTED)

#: Section headers may carry a parenthesized count (e.g. "### IN (9)").
_HEADER_RE = re.compile(r"^### (IN|DEPENDENCY_ONLY|DEFERRED|REJECTED)\b")
_ANY_HEADER_RE = re.compile(r"^### ([A-Z_]+)")
_ROW_RE = re.compile(r"^\| (P2-C\d+) \|")
_CLINICAL_RE = re.compile(r"^\| P2-CLINICAL \|")
_ID_RE = re.compile(r"P2-C\d+|P2-CLINICAL")
_WP_CELL_RE = re.compile(r"P2-\d{2}")


@dataclass(frozen=True)
class ScopeItem:
    """One governed scope row with its single classification."""

    scope_id: str
    classification: str
    maps_to: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScopeRegister:
    """Parsed scope register with taxonomy checks."""

    items: tuple[ScopeItem, ...]
    classification_counts: dict[str, int]
    p2c_rows: int
    clinical_guard: bool
    duplicates: tuple[str, ...]
    unclassified: tuple[str, ...]
    illegal: tuple[str, ...]

    @property
    def total_classified_rows(self) -> int:
        """Complete classified row count (15 P2-C* + 1 P2-CLINICAL guard)."""
        return self.p2c_rows + (1 if self.clinical_guard else 0)

    @property
    def valid(self) -> bool:
        return not self.duplicates and not self.unclassified and not self.illegal

    def classification_of(self, scope_id: str) -> str | None:
        """Classification of ``scope_id`` or None when unknown."""
        for item in self.items:
            if item.scope_id == scope_id:
                return item.classification
        if scope_id == "P2-CLINICAL" and self.clinical_guard:
            return REJECTED
        return None


def _extract_maps_to(line: str) -> tuple[str, ...]:
    """WP targets from the final table cell of an IN-scope row."""
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 3:
        return ()
    return tuple(_WP_CELL_RE.findall(cells[-2]))


def parse_scope_register(path: Path) -> ScopeRegister:
    """Parse and classify every governed scope row in the frozen register."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    section: str | None = None
    items: list[ScopeItem] = []
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    clinical_guard = False
    illegal: list[str] = []

    for line in lines:
        header = _HEADER_RE.match(line)
        if header:
            section = header.group(1)
            continue
        if section is None:
            continue
        if _CLINICAL_RE.match(line):
            if section != REJECTED:
                duplicates.append("P2-CLINICAL")
            else:
                clinical_guard = True
            continue
        row = _ROW_RE.match(line)
        if row is None:
            continue
        scope_id = row.group(1)
        if scope_id in seen:
            duplicates.append(scope_id)
            continue
        seen[scope_id] = section
        maps_to = _extract_maps_to(line) if section == IN else ()
        items.append(ScopeItem(scope_id=scope_id, classification=section, maps_to=maps_to))

    # Illegal classification: a section header outside the frozen vocabulary.
    for line in lines:
        header = _ANY_HEADER_RE.match(line)
        if header and header.group(1) not in CLASSIFICATIONS:
            illegal.append(header.group(1))

    referenced = set(_ID_RE.findall(text))
    classified = set(seen)
    if clinical_guard:
        classified.add("P2-CLINICAL")
    unclassified = tuple(sorted(referenced - classified))

    counts: dict[str, int] = {c: 0 for c in CLASSIFICATIONS}
    for item in items:
        counts[item.classification] += 1

    return ScopeRegister(
        items=tuple(items),
        classification_counts=counts,
        p2c_rows=len(items),
        clinical_guard=clinical_guard,
        duplicates=tuple(sorted(set(duplicates))),
        unclassified=unclassified,
        illegal=tuple(sorted(set(illegal))),
    )
