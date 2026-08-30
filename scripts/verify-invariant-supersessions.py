#!/usr/bin/env python3
"""HFM Phase 2 invariant-supersession verifier.

Validates docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md
against the supersession contract:

  - register parses; ASSERTION_ID unique;
  - every entry has a valid invariant class (H/P/C/B/A);
  - only CLASS H may be superseded (P/B/C/A supersession attempts FAIL);
  - all required fields complete; no N/A in supersession-critical fields of
    superseded entries;
  - superseding authority references a real frozen governance file;
  - historical replay baseline + command present and valid;
  - current replacement test present and existing;
  - effective commit/baseline is a valid Git object;
  - no self-supersession, no cycles in the supersession chain.

The verifier is migration-agnostic (no 0013/0014 literals): it generalizes
to any future authorized evolution (0014 -> 0015 -> ...) without framework
changes. Exit 0 on success, 1 on any failure.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

#: Frozen supersession schema (§ fields of the register contract).
REQUIRED_FIELDS: tuple[str, ...] = (
    "ASSERTION_ID",
    "CLASS",
    "HISTORICAL_TEST",
    "INTRODUCED_AT_BASELINE",
    "HISTORICAL_EXPECTATION",
    "SUPERSEDED_BY_ASSERTION_ID",
    "SUPERSEDING_AUTHORITY",
    "EFFECTIVE_FROM",
    "CURRENT_REPLACEMENT_TEST",
    "HISTORICAL_REPLAY_BASELINE",
    "HISTORICAL_REPLAY_COMMAND",
    "RATIONALE",
    "STATUS",
)

VALID_CLASSES: tuple[str, ...] = ("H", "P", "C", "B", "A")
VALID_STATUSES: tuple[str, ...] = ("ACTIVE", "SUPERSEDED")

#: Only CLASS H may be superseded. P/B/C/A are permanent or current and are
#: never eligible for supersession.
SUPERSEDABLE_CLASSES: tuple[str, ...] = ("H",)

#: Fields that must carry a real value (not "N/A") for a superseded entry.
SUPERSESSION_REQUIRED: tuple[str, ...] = (
    "SUPERSEDED_BY_ASSERTION_ID",
    "SUPERSEDING_AUTHORITY",
    "EFFECTIVE_FROM",
    "CURRENT_REPLACEMENT_TEST",
    "HISTORICAL_REPLAY_BASELINE",
    "HISTORICAL_REPLAY_COMMAND",
)

_SECTION_RE = re.compile(r"^### (ASN-[A-Z0-9-]+)$", re.M)
_FIELD_RE = re.compile(r"^([A-Z_]+): (.*)$", re.M)
_AUTHORITY_FILE_RE = re.compile(r"([A-Za-z0-9._-]+\.md)")
_GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class Entry:
    assertion_id: str
    fields: dict[str, str]

    def field(self, name: str) -> str:
        return self.fields.get(name, "").strip()

    @property
    def cls(self) -> str:
        return self.field("CLASS")

    @property
    def status(self) -> str:
        return self.field("STATUS")

    @property
    def superseded(self) -> bool:
        return self.status == "SUPERSEDED"


@dataclass
class VerificationReport:
    errors: list[str] = field(default_factory=list)
    entries: dict[str, Entry] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors


def git_object_exists(repo_root: Path, sha: str) -> bool:
    """True when the 40-hex value resolves to an object in the repo."""
    if not _GIT_OBJECT_RE.match(sha):
        return False
    result = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def parse_register(path: Path) -> tuple[dict[str, Entry], list[str]]:
    text = path.read_text(encoding="utf-8")
    sections = list(_SECTION_RE.finditer(text))
    entries: dict[str, Entry] = {}
    duplicates: list[str] = []
    for i, match in enumerate(sections):
        start = match.end()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
        body = text[start:end]
        fields = dict(_FIELD_RE.findall(body))
        assertion_id = match.group(1)
        if assertion_id in entries:
            duplicates.append(assertion_id)
        entries[assertion_id] = Entry(assertion_id=assertion_id, fields=fields)
    return entries, duplicates


def validate(repo_root: Path, register_path: Path) -> VerificationReport:
    report = VerificationReport()
    if not register_path.is_file():
        report.errors.append(f"register does not exist: {register_path}")
        return report

    entries, duplicates = parse_register(register_path)
    report.entries = entries
    if not entries:
        report.errors.append("register contains no assertions")
        return report

    # 1. unique ASSERTION_ID (duplicate sections detected at parse time)
    if duplicates:
        report.errors.append(f"duplicate ASSERTION_ID present: {sorted(set(duplicates))}")

    for entry in entries.values():
        # 2. valid class and status
        if entry.cls not in VALID_CLASSES:
            report.errors.append(f"{entry.assertion_id}: invalid class {entry.cls!r}")
        if entry.status not in VALID_STATUSES:
            report.errors.append(f"{entry.assertion_id}: invalid status {entry.status!r}")

        # 3. required fields complete
        missing = [f for f in REQUIRED_FIELDS if f not in entry.fields]
        if missing:
            report.errors.append(f"{entry.assertion_id}: missing required fields {missing}")

        # 4. only CLASS H may be superseded
        if entry.superseded and entry.cls not in SUPERSEDABLE_CLASSES:
            report.errors.append(
                f"{entry.assertion_id}: {entry.cls} supersession attempt is forbidden"
            )

        # 5. supersession-critical fields must be real for superseded entries
        if entry.superseded:
            for req in SUPERSESSION_REQUIRED:
                value = entry.field(req)
                if not value or value == "N/A":
                    report.errors.append(
                        f"{entry.assertion_id}: supersession field {req} missing or N/A"
                    )
            # 6. self-supersession
            if entry.field("SUPERSEDED_BY_ASSERTION_ID") == entry.assertion_id:
                report.errors.append(f"{entry.assertion_id}: self-supersession")

        # 7. active entries must not carry a supersession binding
        if not entry.superseded and entry.field("SUPERSEDED_BY_ASSERTION_ID") not in ("", "N/A"):
            report.errors.append(
                f"{entry.assertion_id}: active entry carries SUPERSEDED_BY_ASSERTION_ID"
            )

    # 8. supersession targets exist; no cycles
    chain: dict[str, str] = {}
    for entry in entries.values():
        if entry.superseded:
            target = entry.field("SUPERSEDED_BY_ASSERTION_ID")
            if target in entries and target != entry.assertion_id:
                chain[entry.assertion_id] = target
            else:
                report.errors.append(
                    f"{entry.assertion_id}: supersession target {target!r} does not exist"
                )

    for start in chain:
        visited: set[str] = set()
        current = start
        while current in chain:
            if current in visited:
                report.errors.append(f"supersession cycle involving {current}")
                break
            visited.add(current)
            current = chain[current]

    for entry in entries.values():
        if not entry.superseded:
            continue
        # 9. authority reference exists (frozen governance file + module text)
        authority = entry.field("SUPERSEDING_AUTHORITY")
        cited = _AUTHORITY_FILE_RE.search(authority)
        if cited:
            authority_path = repo_root / "docs" / "governance" / cited.group(1)
            if not authority_path.is_file():
                report.errors.append(
                    f"{entry.assertion_id}: authority file not found: {cited.group(1)}"
                )
        else:
            report.errors.append(f"{entry.assertion_id}: authority reference missing")
        # 10. effective commit valid
        if not git_object_exists(repo_root, entry.field("EFFECTIVE_FROM")):
            report.errors.append(
                f"{entry.assertion_id}: effective commit {entry.field('EFFECTIVE_FROM')} invalid"
            )
        # 11. historical replay binding present and valid
        replay_base = entry.field("HISTORICAL_REPLAY_BASELINE")
        if not git_object_exists(repo_root, replay_base):
            report.errors.append(f"{entry.assertion_id}: replay baseline {replay_base} invalid")
        if not entry.field("HISTORICAL_REPLAY_COMMAND"):
            report.errors.append(f"{entry.assertion_id}: replay command missing")
        # 12. current replacement test exists
        replacement = entry.field("CURRENT_REPLACEMENT_TEST")
        if not replacement:
            report.errors.append(f"{entry.assertion_id}: current replacement test missing")
        else:
            if "::" in replacement:
                test_file, test_id = replacement.split("::", 1)
            else:
                test_file, test_id = replacement, None
            test_path = repo_root / test_file
            if not test_path.is_file():
                report.errors.append(
                    f"{entry.assertion_id}: replacement test file not found: {test_file}"
                )
            elif test_id and test_id not in test_path.read_text(encoding="utf-8", errors="replace"):
                report.errors.append(
                    f"{entry.assertion_id}: replacement test id not found: {test_id}"
                )

    # 13. introduced-at baseline valid for every entry that carries one
    for entry in entries.values():
        intro = entry.field("INTRODUCED_AT_BASELINE")
        if intro and intro != "N/A" and not git_object_exists(repo_root, intro):
            report.errors.append(f"{entry.assertion_id}: introduced-at baseline {intro} invalid")

    return report


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    register = (
        repo_root / "docs" / "governance" / "HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md"
    )
    report = validate(repo_root, register)
    for error in report.errors:
        print(f"SUPERSESSION_ERROR: {error}")
    print(
        f"SUPERSESSION_REGISTER=FAIL ({len(report.errors)} error(s))"
        if report.errors
        else "SUPERSESSION_REGISTER=PASS"
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
