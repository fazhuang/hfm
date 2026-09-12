#!/usr/bin/env python3
"""HFM secret boundary scanner (P1-07 correction).

Fail-closed scan over tracked files for committed secrets. Detection
classes: private keys, cloud/token credentials, quoted literal
password/secret/token values, and URL-embedded credentials. Placeholder
and example values are allowed only through explicit safe patterns.
Secret values are never printed — only file/class/reason.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

#: Explicitly safe placeholder values (allowed by the environment contract).
SAFE_VALUES: tuple[re.Pattern[str], ...] = (
    re.compile(r"change-?me", re.IGNORECASE),
    re.compile(r"changeme", re.IGNORECASE),
    re.compile(r"example", re.IGNORECASE),
    re.compile(r"your[-_]?token[-_]?here", re.IGNORECASE),
    re.compile(r"xxx+", re.IGNORECASE),
    re.compile(r"hfm"),  # local dev default password (hfm) is a contract default
)

#: Exact tracked secret-scanner test-fixture paths (P1-07 synthetic harness).
#: These files deliberately embed synthetic detection fixtures to prove the
#: scanner detects each secret class. The exemption is EXACT-PATH and
#: fixture-scoped: scan_file() is never weakened, no broad exclusion, and
#: every other tracked file remains fail-closed.
EXEMPT_TRACKED_SECRET_FIXTURE_PATHS: frozenset[str] = frozenset(
    {"scripts/test-check-secrets.sh"}
)

#: Detection classes: (name, pattern). The literal is a *value* that looks
#: like a secret, not a variable name.
CLASSES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key", re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    (
        "literal-password",
        re.compile(r"""(?i)(?:password|passwd)\s*"?\s*[=:]\s*["'][^"']{8,}["']"""),
    ),
    (
        "literal-secret-token",
        re.compile(
            r"""(?i)(?:secret|api[_-]?key|token)\s*"?\s*[=:]\s*["'][A-Za-z0-9._-]{12,}["']"""
        ),
    ),
    (
        "url-embedded-credentials",
        re.compile(
            r"[a-z][a-z0-9+.-]*://[^:@/ ]+:(?!change-?me@|changeme@|CHANGEME@|example@)[^:@/ ]+@"
        ),
    ),
)


@dataclass(frozen=True)
class Finding:
    path: str
    cls: str
    reason: str
    line: int


def is_safe_literal(value: str) -> bool:
    return any(pattern.search(value) for pattern in SAFE_VALUES)


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line_no, line in enumerate(text.splitlines(), start=1):
        for cls, pattern in CLASSES:
            for match in pattern.finditer(line):
                value = match.group(0)
                # URL-embedded credentials: exempt placeholder passwords.
                if cls == "url-embedded-credentials" and is_safe_literal(value):
                    continue
                # Literal classes: exempt placeholder values.
                if cls in ("literal-password", "literal-secret-token"):
                    quoted = re.search(r"[\'\"]([^\'\"]+)[\'\"]", value)
                    if quoted and is_safe_literal(quoted.group(1)):
                        continue
                findings.append(
                    Finding(
                        path=str(path),
                        cls=cls,
                        reason=f"{cls} at line {line_no}",
                        line=line_no,
                    )
                )
                break
    return findings


def is_exempt_tracked_fixture(repo_root: Path, file: Path) -> bool:
    """Exact-path exemption: only the named tracked fixture path is exempt.

    Adversarial semantics: a similarly named file, a nested path, or a
    renamed file are NOT exempt; membership is an exact repo-relative match.
    """
    try:
        rel = file.relative_to(repo_root).as_posix()
    except ValueError:
        return False
    return rel in EXEMPT_TRACKED_SECRET_FIXTURE_PATHS


def tracked_files(repo_root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [repo_root / name for name in out.stdout.splitlines() if name]


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    findings: list[Finding] = []
    for file in tracked_files(repo_root):
        if not file.is_file():
            continue
        if is_exempt_tracked_fixture(repo_root, file):
            continue  # exact-path secret-scanner test fixture (synthetic only)
        if file.name.endswith(".env.example"):
            continue  # placeholder contracts only
        findings.extend(scan_file(file))

    for finding in findings:
        print(
            f"SECRET FOUND: {finding.path} (class={finding.cls}, line={finding.line})"
        )
    if findings:
        print(f"SECRET_BOUNDARY=FAIL ({len(findings)} finding(s))")
        return 1
    print("SECRET_BOUNDARY=PASS (no committed secrets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
