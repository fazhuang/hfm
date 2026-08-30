#!/usr/bin/env python3
"""P2-10 reuse-adjudication machine parser (P1-09 correction).

Parses docs/governance/HFM-PHASE2-HFB-REUSE-ADJUDICATION-v1.md and verifies:
  - total items = 27; no duplicate item IDs;
  - every item has exactly one verdict from the frozen taxonomy
    (PORT/ADAPT/REFERENCE_ONLY/DEFER/REJECT);
  - taxonomy counts match the frozen accounting
    (PORT 1, ADAPT 5, REFERENCE_ONLY 13, DEFER 5, REJECT 3);
  - unclassified = 0; invalid taxonomy = 0;
  - every row carries the required fields: source asset, classification,
    reason, evidence/reference, runtime-coupling implication,
    migration implication.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

TAXONOMY: tuple[str, ...] = ("PORT", "ADAPT", "REFERENCE_ONLY", "DEFER", "REJECT")
EXPECTED_COUNTS: dict[str, int] = {
    "PORT": 1,
    "ADAPT": 5,
    "REFERENCE_ONLY": 13,
    "DEFER": 5,
    "REJECT": 3,
}
EXPECTED_TOTAL = 27

#: Register table column headers (frozen register).
REQUIRED_HEADERS = (
    "ID",
    "Source asset",
    "Decision",
    "Reason",
    "Runtime coupling",
    "Migration impact",
    "Security impact",
    "Reuse destination",
    "Evidence",
)


@dataclass
class RegisterRow:
    values: dict[str, str]

    def field(self, name: str) -> str:
        return self.values.get(name, "").strip()


@dataclass
class AdjudicationReport:
    rows: list[RegisterRow] = field(default_factory=list)
    total: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    duplicates: list[str] = field(default_factory=list)
    unclassified: list[str] = field(default_factory=list)
    invalid_taxonomy: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    runtime_coupling: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (
            self.duplicates
            or self.unclassified
            or self.invalid_taxonomy
            or self.missing_fields
            or self.runtime_coupling
        )


def parse_register(path: Path) -> AdjudicationReport:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = next(
        (i for i, line in enumerate(lines) if "| ID |" in line and "| Decision |" in line),
        None,
    )
    if header_index is None:
        raise ValueError("adjudication register header not found")

    headers = [cell.strip() for cell in lines[header_index].split("|")[1:-1]]
    for required in REQUIRED_HEADERS:
        if required not in headers:
            raise ValueError(f"adjudication register missing required column: {required}")

    report = AdjudicationReport()
    seen: set[str] = set()
    for line in lines[header_index + 2 :]:
        if not line.startswith("| ADJ-"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < len(headers):
            continue
        row = RegisterRow(dict(zip(headers, cells, strict=True)))
        report.rows.append(row)

        item_id = row.field("ID")
        if item_id in seen:
            report.duplicates.append(item_id)
        seen.add(item_id)

        verdict = row.field("Decision")
        if verdict not in TAXONOMY:
            report.invalid_taxonomy.append(item_id)
        elif verdict in ("PORT", "ADAPT", "REFERENCE_ONLY", "DEFER", "REJECT"):
            report.counts[verdict] = report.counts.get(verdict, 0) + 1

        for required in ("Source asset", "Reason", "Evidence", "Reuse destination"):
            if not row.field(required):
                report.missing_fields.append(f"{item_id}:{required}")

        coupling = row.field("Runtime coupling")
        if coupling != "0":
            report.runtime_coupling.append(f"{item_id}:{coupling}")

    report.total = len(report.rows)
    return report


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    register = repo_root / "docs" / "governance" / "HFM-PHASE2-HFB-REUSE-ADJUDICATION-v1.md"
    report = parse_register(register)

    print(f"total={report.total} (expect {EXPECTED_TOTAL})")
    print(f"counts={dict(sorted(report.counts.items()))} (expect {EXPECTED_COUNTS})")
    print(f"duplicates={report.duplicates or 0}")
    print(f"unclassified={report.unclassified or 0}")
    print(f"invalid_taxonomy={report.invalid_taxonomy or 0}")
    print(f"missing_fields={report.missing_fields or 0}")
    print(f"runtime_coupling={report.runtime_coupling or 0}")

    failures: list[str] = []
    if report.total != EXPECTED_TOTAL:
        failures.append(f"total {report.total} != {EXPECTED_TOTAL}")
    for key, expected in EXPECTED_COUNTS.items():
        if report.counts.get(key, 0) != expected:
            failures.append(f"{key} {report.counts.get(key, 0)} != {expected}")
    if not report.ok:
        failures.append("duplicates/unclassified/invalid/missing/runtime-coupling present")

    if failures:
        print(f"ADJUDICATION_MACHINE_PARSE=FAIL ({'; '.join(failures)})")
        return 1
    print("ADJUDICATION_MACHINE_PARSE=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
