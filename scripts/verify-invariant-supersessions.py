#!/usr/bin/env python3
"""HFM Phase 2 invariant-supersession verifier (hardened).

Validates docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md:

  - strict schema: rejects unknown fields, duplicate fields, malformed
    records, unknown CLASS and unknown STATUS (fail-closed);
  - mechanical counts: derives totals/category/status sums from parsed
    records and requires them to equal the register's DECLARED_* block;
  - authority semantic validation: superseded Class H entries must carry
    AUTHORITY_TYPE / AUTHORITY_ID / AUTHORITY_DOCUMENT; the document must
    exist, the authority id must appear in it, and the type must be one of
    WP_CONTRACT / ADR / ACCEPTED_AMENDMENT;
  - baseline identity/ancestry: INTRODUCED_AT_BASELINE, REPLAY_BASELINE and
    EFFECTIVE_FROM must be valid Git objects; introduced/replay baselines
    must be ancestors of EFFECTIVE_FROM; known baseline roles must match
    their expected commit;
  - supersession graph: unique ids, no self/cycles, every SUPERSEDED
    assertion resolves to exactly one ACTIVE terminal assertion whose
    current replacement test exists;
  - historical replay: machine-executed in an isolated temporary worktree
    (pytest only, argv subprocess, shell=False);
  - current replacement tests: machine-executed (pytest only).

Migration-agnostic: no 0013/0014 literals — the framework generalizes to any
future authorized evolution (0014 -> 0015 -> ...).
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

#: Strict schema — any other field key is rejected (fail-closed).
KNOWN_FIELDS: tuple[str, ...] = (
    "ASSERTION_ID",
    "CLASS",
    "STATUS",
    "HISTORICAL_TEST",
    "INTRODUCED_AT_BASELINE",
    "INTRODUCED_AT_ROLE",
    "HISTORICAL_EXPECTATION",
    "SUPERSEDED_BY_ASSERTION_ID",
    "AUTHORITY_TYPE",
    "AUTHORITY_ID",
    "AUTHORITY_DOCUMENT",
    "EFFECTIVE_FROM",
    "CURRENT_REPLACEMENT_TEST",
    "REPLAY_BASELINE",
    "REPLAY_BASELINE_ROLE",
    "REPLAY_KIND",
    "REPLAY_TEST",
    "RATIONALE",
)

VALID_CLASSES: tuple[str, ...] = ("H", "P", "C", "B", "A")
VALID_STATUSES: tuple[str, ...] = ("ACTIVE", "SUPERSEDED")
SUPERSEDABLE_CLASSES: tuple[str, ...] = ("H",)
ALLOWED_AUTHORITY_TYPES: tuple[str, ...] = ("WP_CONTRACT", "ADR", "ACCEPTED_AMENDMENT")
ALLOWED_REPLAY_KINDS: tuple[str, ...] = ("PYTEST",)

#: Fields required (with a real value) for every entry.
COMMON_REQUIRED: tuple[str, ...] = (
    "ASSERTION_ID",
    "CLASS",
    "STATUS",
    "HISTORICAL_TEST",
    "INTRODUCED_AT_BASELINE",
    "INTRODUCED_AT_ROLE",
    "HISTORICAL_EXPECTATION",
    "RATIONALE",
)

#: Fields required (with a real value, not N/A) for superseded Class H entries.
SUPERSEDED_REQUIRED: tuple[str, ...] = (
    "SUPERSEDED_BY_ASSERTION_ID",
    "AUTHORITY_TYPE",
    "AUTHORITY_ID",
    "AUTHORITY_DOCUMENT",
    "EFFECTIVE_FROM",
    "CURRENT_REPLACEMENT_TEST",
    "REPLAY_BASELINE",
    "REPLAY_BASELINE_ROLE",
    "REPLAY_KIND",
    "REPLAY_TEST",
)

#: Fields that must be N/A for non-superseded entries.
NON_SUPERSEDED_NA: tuple[str, ...] = (
    "SUPERSEDED_BY_ASSERTION_ID",
    "AUTHORITY_TYPE",
    "AUTHORITY_ID",
    "AUTHORITY_DOCUMENT",
    "REPLAY_BASELINE",
    "REPLAY_BASELINE_ROLE",
    "REPLAY_KIND",
    "REPLAY_TEST",
)

#: Formal baseline roles the verifier recognizes (expected commit binding).
BASELINE_ROLES: dict[str, str] = {
    "P2_00_ACCEPTANCE_BASELINE": "bd0d39e76fe5a8289006664514af9250a7f84f14",
    "PHASE1_COMPLETION_BASELINE": "c17be40be6f055498fde11c0042e71d3a1056a7c",
    "P1_12_ACCEPTED_CANDIDATE": "0ed47d648efa1478e999439333dc32d36e080831",
    "P2_05_MIGRATION_COMMIT": "b53c897cfffd287516ecb1ed230df2f8f83687d9",
    "FRONTIER2_CORRECTED_CANDIDATE": "d38f871a230ca56713737b7de82f9111e7e73650",
}

_SECTION_RE = re.compile(r"^### (ASN-[A-Z0-9-]+)$", re.M)
_FIELD_RE = re.compile(r"^([A-Z_]+): (.*)$")
_DECLARED_RE = re.compile(r"^(DECLARED_[A-Z_0-9]+): (\d+)$", re.M)
_GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")
_SAFE_TEST_RE = re.compile(r"^tests/[A-Za-z0-9_./-]+(?:::[A-Za-z0-9_]+)?$")


@dataclass
class Entry:
    assertion_id: str
    fields: dict[str, str]
    duplicate_fields: list[str] = field(default_factory=list)
    malformed_lines: list[str] = field(default_factory=list)

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
    replays_executed: int = 0
    replacements_executed: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


def git(
    args: list[str], repo_root: Path, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Git invocation with argv list only (shell=False)."""
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        check=False,
    )


def git_object_exists(repo_root: Path, sha: str) -> bool:
    if not _GIT_OBJECT_RE.match(sha):
        return False
    return (
        git(
            ["-c", "core.quotePath=false", "cat-file", "-e", f"{sha}^{{commit}}"], repo_root
        ).returncode
        == 0
    )


def is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    if not git_object_exists(repo_root, ancestor) or not git_object_exists(repo_root, descendant):
        return False
    result = git(["merge-base", "--is-ancestor", ancestor, descendant], repo_root)
    return result.returncode == 0


def safe_test_node(repo_root: Path, node: str) -> bool:
    """Repo-relative pytest node id/path only; no traversal, no absolute path.
    Accepts backend-relative ("tests/...") and repo-relative
    ("apps/backend/tests/...") forms and normalizes to backend-relative."""
    normalized = node.removeprefix("apps/backend/")
    if not _SAFE_TEST_RE.match(normalized):
        return False
    path = repo_root / "apps" / "backend" / normalized
    return path.is_file() or path.parent.is_dir()


def parse_register(path: Path) -> tuple[dict[str, Entry], list[str], dict[str, int]]:
    """Parse entries, duplicate section ids, and the DECLARED_* accounting."""
    text = path.read_text(encoding="utf-8")
    sections = list(_SECTION_RE.finditer(text))
    entries: dict[str, Entry] = {}
    duplicates: list[str] = []
    heading_re = re.compile(r"^#{2,3} ", re.M)
    for i, match in enumerate(sections):
        start = match.end()
        end = len(text)
        if i + 1 < len(sections):
            end = sections[i + 1].start()
        else:
            next_heading = heading_re.search(text, start)
            if next_heading:
                end = next_heading.start()
        body = text[start:end]
        fields: dict[str, str] = {}
        duplicate_fields: list[str] = []
        malformed: list[str] = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line == "```":
                continue
            fm = _FIELD_RE.match(line)
            if not fm:
                malformed.append(line)
                continue
            key, value = fm.group(1), fm.group(2).strip()
            if key in fields:
                duplicate_fields.append(key)
            fields[key] = value
        assertion_id = match.group(1)
        if assertion_id in entries:
            duplicates.append(assertion_id)
        entries[assertion_id] = Entry(assertion_id, fields, duplicate_fields, malformed)
    declared = {}
    for m in _DECLARED_RE.finditer(text):
        try:
            declared[m.group(1)] = int(m.group(2))
        except ValueError:
            declared[m.group(1)] = -1
    return entries, duplicates, declared


def validate(repo_root: Path, register_path: Path) -> VerificationReport:
    report = VerificationReport()
    if not register_path.is_file():
        report.errors.append(f"register does not exist: {register_path}")
        return report

    entries, duplicates, declared = parse_register(register_path)
    report.entries = entries
    if not entries:
        report.errors.append("register contains no assertions")
        return report
    if duplicates:
        report.errors.append(f"duplicate ASSERTION_ID present: {sorted(set(duplicates))}")

    # ---- strict schema + mechanical counts ----
    class_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for entry in entries.values():
        for req in COMMON_REQUIRED:
            if req not in entry.fields or not entry.field(req):
                report.errors.append(f"{entry.assertion_id}: missing required field {req}")
        if entry.duplicate_fields:
            report.errors.append(
                f"{entry.assertion_id}: duplicate fields {sorted(set(entry.duplicate_fields))}"
            )
        if entry.malformed_lines:
            report.errors.append(
                f"{entry.assertion_id}: malformed record lines {entry.malformed_lines[:2]}"
            )
        unknown = sorted(set(entry.fields) - set(KNOWN_FIELDS))
        if unknown:
            report.errors.append(f"{entry.assertion_id}: unknown fields {unknown}")
        if entry.cls not in VALID_CLASSES:
            report.errors.append(f"{entry.assertion_id}: unknown CLASS {entry.cls!r}")
        else:
            class_counts[entry.cls] = class_counts.get(entry.cls, 0) + 1
        if entry.status not in VALID_STATUSES:
            report.errors.append(f"{entry.assertion_id}: unknown STATUS {entry.status!r}")
        else:
            status_counts[entry.status] = status_counts.get(entry.status, 0) + 1

        if entry.superseded and entry.cls not in SUPERSEDABLE_CLASSES:
            report.errors.append(
                f"{entry.assertion_id}: {entry.cls} supersession attempt is forbidden"
            )
        if entry.superseded:
            for req in SUPERSEDED_REQUIRED:
                value = entry.field(req)
                if not value or value == "N/A":
                    report.errors.append(
                        f"{entry.assertion_id}: supersession field {req} missing or N/A"
                    )
            if entry.field("SUPERSEDED_BY_ASSERTION_ID") == entry.assertion_id:
                report.errors.append(f"{entry.assertion_id}: self-supersession")
        else:
            for req in NON_SUPERSEDED_NA:
                value = entry.field(req)
                if value and value != "N/A":
                    report.errors.append(
                        f"{entry.assertion_id}: non-superseded entry carries {req}"
                    )

    # ---- declared-accounting reconciliation (P1-01) ----
    actual_total = len(entries)
    if declared:
        if declared.get("DECLARED_TOTAL") != actual_total:
            report.errors.append(
                f"declared total {declared.get('DECLARED_TOTAL')} != actual rows {actual_total}"
            )
        for cls in VALID_CLASSES:
            key = f"DECLARED_CLASS_{cls}"
            if key in declared and declared[key] != class_counts.get(cls, 0):
                report.errors.append(
                    f"declared {key} {declared[key]} != actual {class_counts.get(cls, 0)}"
                )
        for status in VALID_STATUSES:
            key = f"DECLARED_{status}"
            if key in declared and declared[key] != status_counts.get(status, 0):
                report.errors.append(
                    f"declared {key} {declared[key]} != actual {status_counts.get(status, 0)}"
                )
    if sum(class_counts.values()) != actual_total:
        report.errors.append("category sum != total")
    if sum(status_counts.values()) != actual_total:
        report.errors.append("status sum != total")

    # ---- authority semantic validation (P1-02) ----
    for entry in entries.values():
        if not entry.superseded:
            continue
        a_type = entry.field("AUTHORITY_TYPE")
        a_id = entry.field("AUTHORITY_ID")
        a_doc = entry.field("AUTHORITY_DOCUMENT")
        if a_type not in ALLOWED_AUTHORITY_TYPES:
            report.errors.append(f"{entry.assertion_id}: disallowed authority type {a_type!r}")
        doc_path = repo_root / a_doc
        if not doc_path.is_file():
            report.errors.append(f"{entry.assertion_id}: authority document not found: {a_doc}")
        else:
            doc_text = doc_path.read_text(encoding="utf-8", errors="replace")
            if not re.search(rf"\b{re.escape(a_id)}\b", doc_text):
                report.errors.append(
                    f"{entry.assertion_id}: authority id {a_id!r} not present in {a_doc}"
                )

    # ---- baseline identity/ancestry (P1-03) ----
    for entry in entries.values():
        intro = entry.field("INTRODUCED_AT_BASELINE")
        if not intro or intro == "N/A":
            report.errors.append(f"{entry.assertion_id}: INTRODUCED_AT_BASELINE required")
        elif not git_object_exists(repo_root, intro):
            report.errors.append(
                f"{entry.assertion_id}: introduced-at baseline {intro} does not exist"
            )
        role = entry.field("INTRODUCED_AT_ROLE")
        if role in BASELINE_ROLES and BASELINE_ROLES[role] != intro:
            report.errors.append(
                f"{entry.assertion_id}: introduced-at role {role} bound to wrong commit"
            )
        if entry.superseded:
            effective = entry.field("EFFECTIVE_FROM")
            replay_base = entry.field("REPLAY_BASELINE")
            replay_role = entry.field("REPLAY_BASELINE_ROLE")
            if not git_object_exists(repo_root, effective):
                report.errors.append(
                    f"{entry.assertion_id}: EFFECTIVE_FROM {effective} does not exist"
                )
            else:
                for label, base in (("introduced-at", intro), ("replay", replay_base)):
                    if base and base != "N/A" and not is_ancestor(repo_root, base, effective):
                        report.errors.append(
                            f"{entry.assertion_id}: {label} baseline {base} not an ancestor"
                            f" of effective {effective}"
                        )
            if replay_role in BASELINE_ROLES and BASELINE_ROLES[replay_role] != replay_base:
                report.errors.append(
                    f"{entry.assertion_id}: replay role {replay_role} bound to wrong commit"
                )

    # ---- supersession graph + active terminal (P1-05) ----
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
        if current not in chain:
            terminal = entries.get(current)
            if terminal is None:
                report.errors.append(f"{start}: missing active terminal")
            elif terminal.status != "ACTIVE":
                report.errors.append(f"{start}: inactive terminal {current}")
            elif terminal.cls not in ("C", "H", "A"):
                report.errors.append(
                    f"{start}: terminal {current} has non-terminal class {terminal.cls}"
                )
            else:
                replacement = terminal.field("CURRENT_REPLACEMENT_TEST")
                if not replacement or replacement == "N/A":
                    report.errors.append(f"{start}: terminal {current} lacks replacement test")
                elif not safe_test_node(repo_root, replacement):
                    report.errors.append(
                        f"{start}: terminal {current} replacement test invalid: {replacement}"
                    )

    # ---- replay / replacement binding sanity (execution happens separately) ----
    for entry in entries.values():
        if not entry.superseded:
            continue
        if entry.field("REPLAY_KIND") not in ALLOWED_REPLAY_KINDS:
            report.errors.append(f"{entry.assertion_id}: disallowed replay kind")
        if not safe_test_node(repo_root, entry.field("REPLAY_TEST")):
            report.errors.append(
                f"{entry.assertion_id}: unsafe replay test node {entry.field('REPLAY_TEST')!r}"
            )
        if not safe_test_node(repo_root, entry.field("CURRENT_REPLACEMENT_TEST")):
            node = entry.field("CURRENT_REPLACEMENT_TEST")
            report.errors.append(f"{entry.assertion_id}: unsafe replacement test node {node!r}")
    return report


def _run_pytest(
    repo_root: Path, backend_dir: Path, node: str, timeout: int = 300
) -> subprocess.CompletedProcess[str]:
    """Execute a pytest node inside the given backend dir (argv only, no shell)."""
    node = node.removeprefix("apps/backend/")
    python = repo_root / "apps" / "backend" / ".venv" / "bin" / "python"
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONPATH": str(backend_dir / "src"),
    }
    return subprocess.run(
        [str(python), "-m", "pytest", node, "-q"],
        capture_output=True,
        text=True,
        cwd=str(backend_dir),
        env=env,
        timeout=timeout,
        check=False,
    )


def execute_replays(repo_root: Path, report: VerificationReport, register_path: Path) -> None:
    """Machine-execute every registered historical replay in an isolated worktree."""
    entries, _, _ = parse_register(register_path)
    for entry in entries.values():
        if not entry.superseded:
            continue
        baseline = entry.field("REPLAY_BASELINE")
        node = entry.field("REPLAY_TEST")
        if not git_object_exists(repo_root, baseline) or not safe_test_node(repo_root, node):
            report.errors.append(f"{entry.assertion_id}: replay not executable")
            continue
        with tempfile.TemporaryDirectory(prefix="hfm-replay-") as tmp:
            worktree = Path(tmp) / "wt"
            add = git(["worktree", "add", "--detach", str(worktree), baseline], repo_root)
            if add.returncode != 0:
                report.errors.append(f"{entry.assertion_id}: replay worktree creation failed")
                continue
            try:
                result = _run_pytest(repo_root, worktree / "apps" / "backend", node)
                report.replays_executed += 1
                if result.returncode != 0:
                    report.errors.append(
                        f"HISTORICAL_REPLAY_FAILURE {entry.assertion_id}: exit {result.returncode}"
                    )
            finally:
                git(["worktree", "remove", "--force", str(worktree)], repo_root)


def execute_replacements(repo_root: Path, report: VerificationReport, register_path: Path) -> None:
    """Machine-execute the current replacement tests of active terminals."""
    backend = repo_root / "apps" / "backend"
    entries, _, _ = parse_register(register_path)
    for entry in entries.values():
        if entry.status != "ACTIVE":
            continue
        node = entry.field("CURRENT_REPLACEMENT_TEST")
        if not node or node == "N/A" or not safe_test_node(repo_root, node):
            continue
        try:
            result = _run_pytest(repo_root, backend, node)
            report.replacements_executed += 1
            if result.returncode != 0:
                report.errors.append(
                    f"REPLACEMENT_TEST_FAILURE {entry.assertion_id}: exit {result.returncode}"
                )
        except subprocess.TimeoutExpired:
            report.errors.append(f"REPLACEMENT_TEST_TIMEOUT {entry.assertion_id}")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    register = (
        repo_root / "docs" / "governance" / "HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md"
    )
    report = validate(repo_root, register)
    if report.errors:
        for error in report.errors:
            print(f"SUPERSESSION_ERROR: {error}")
        print("SUPERSESSION_REGISTER=FAIL")
        return 1
    execute_replays(repo_root, report, register)
    execute_replacements(repo_root, report, register)
    entries, _, _ = parse_register(register)
    class_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for entry in entries.values():
        class_counts[entry.cls] = class_counts.get(entry.cls, 0) + 1
        status_counts[entry.status] = status_counts.get(entry.status, 0) + 1
    print(
        f"entries={len(entries)} classes={dict(sorted(class_counts.items()))} "
        f"statuses={dict(sorted(status_counts.items()))}"
    )
    print(f"replays_executed={report.replays_executed}")
    print(f"replacement_tests_executed={report.replacements_executed}")
    if report.errors:
        for error in report.errors:
            print(f"SUPERSESSION_ERROR: {error}")
        print("SUPERSESSION_REGISTER=FAIL")
        return 1
    print("SUPERSESSION_REGISTER=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
