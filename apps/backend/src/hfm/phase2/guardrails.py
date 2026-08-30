"""Phase-2 negative-boundary guardrails (P2-00 contract verifier).

Machine guards for the frozen negative states: Clinical=REJECTED,
AI/Display/3D/VR/XR/virtual-training=DEFERRED, credential migration=
DO_NOT_MIGRATE, production HFB import=NOT AUTHORIZED, M4-M7=NOT AUTHORIZED,
and HFB runtime zero-coupling.

Detection targets imports, registrations, service bindings and declared
implementation modules rather than naive whole-repo word greps, and is
scoped to the Phase-2 implementation surface so the verifier's own
vocabulary declarations cannot self-trigger.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: Frozen negative-boundary states (acceptance archive + migration contract).
CLINICAL_STATE = "REJECTED"
AI_STATE = "DEFERRED"
DISPLAY_STATE = "DEFERRED"
XR_STATE = "DEFERRED"
CREDENTIAL_MIGRATION_STATE = "DO_NOT_MIGRATE"
PRODUCTION_HFB_IMPORT_STATE = "NOT AUTHORIZED"
M4_M7_STATE = "NOT AUTHORIZED"

#: Frozen accepted Phase-2 ADR decisions (governance acceptance archive).
ACCEPTED_ADRS: frozenset[str] = frozenset({"ADR-P2-01", "ADR-P2-02"})

#: ADR gate per gated WP (frozen DAG rows: required-evidence column).
ADR_GATES: dict[str, str] = {"P2-05": "ADR-P2-01", "P2-07": "ADR-P2-02"}

#: HFB runtime coupling: import statements only (line-anchored), so negative
#: assertions inside string literals never trigger a false positive.
_HFB_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+hfb(?:_|\b)", re.M)

#: Forbidden-capability imports on the Phase-2 implementation surface.
_FORBIDDEN_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+("
    r"torch|openai|anthropic|langchain|transformers|"
    r"three|threejs|webgl|webxr|aframe|"
    r"hfb[a-z_]*"
    r")\b",
    re.M | re.I,
)

#: Clinical / virtual-training surface markers (paths, routes, bindings).
_CLINICAL_MARKER_RE = re.compile(
    r"clinical|diagnos|prescription|treatment_recommend|acupoint_recommend|virtual_train",
    re.I,
)

#: Display / exhibition implementation markers.
_DISPLAY_MARKER_RE = re.compile(r"display_mode|exhibition_mode", re.I)

#: Production-import execution markers (never authorized under P2-00).
_PRODUCTION_IMPORT_RE = re.compile(
    r"production_import|execute_production_import|alembic\.command\.(?:upgrade|downgrade)",
    re.I,
)

#: Credential / session migration markers (MC-12 DO_NOT_MIGRATE).
_CREDENTIAL_MIGRATION_RE = re.compile(
    r"credential.*migrat|migrat.*(?:password|credential)|session.*migrat",
    re.I,
)

#: Alembic revision declarations inside migration files.
_REVISION_RE = re.compile(r'revision\s*=\s*["\']([^"\']+)["\']')

#: Verifier package files that declare the guard vocabulary itself. The
#: marker scan covers non-verifier Phase-2 implementation modules only: the
#: verifier is the guard, so its own vocabulary declarations (docstrings and
#: constant names such as ``P2-CLINICAL``) are not implementations. Failure
#: detection is proven by the tests against synthetic violating modules.
_VERIFIER_FILES: frozenset[str] = frozenset(
    {"guardrails.py", "scope.py", "traceability.py", "contract.py", "__init__.py"}
)


@dataclass(frozen=True)
class GuardrailReport:
    """Negative-boundary guard state."""

    clinical: str
    ai: str
    display: str
    xr: str
    credential_migration: str
    production_hfb_import: str
    m4_m7: str
    accepted_adrs: frozenset[str]
    adr_gates: dict[str, str]
    adr_gate_violations: tuple[str, ...]
    hfb_coupling_findings: tuple[str, ...]
    forbidden_marker_findings: tuple[str, ...]
    migration_revisions: tuple[str, ...]
    migration_heads: tuple[str, ...]

    @property
    def hfb_coupling_clean(self) -> bool:
        return not self.hfb_coupling_findings

    @property
    def marker_clean(self) -> bool:
        return not self.forbidden_marker_findings

    @property
    def migration_ok(self) -> bool:
        expected = {f"{i:04d}" for i in range(1, 15)}  # 0001..0014 (P2-05 authorized migration)
        return set(self.migration_revisions) == expected and len(self.migration_heads) == 1

    @property
    def ok(self) -> bool:
        return (
            self.clinical == CLINICAL_STATE
            and self.ai == AI_STATE
            and self.display == DISPLAY_STATE
            and self.xr == XR_STATE
            and self.credential_migration == CREDENTIAL_MIGRATION_STATE
            and self.production_hfb_import == PRODUCTION_HFB_IMPORT_STATE
            and self.m4_m7 == M4_M7_STATE
            and not self.adr_gate_violations
            and self.hfb_coupling_clean
            and self.marker_clean
            and self.migration_ok
        )


def scan_hfb_coupling(root: Path) -> tuple[str, ...]:
    """Line-anchored HFB runtime import scan over ``*.py`` under ``root``."""
    findings: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if _HFB_IMPORT_RE.search(text):
            findings.append(str(path.relative_to(root)))
    return tuple(findings)


def scan_forbidden_markers(
    root: Path, *, excluded: frozenset[str] = frozenset()
) -> tuple[str, ...]:
    """Forbidden-capability implementation scan over Phase-2 paths.

    Targets imports, module/route/service declarations, and path names.
    ``excluded`` names (e.g. the verifier's own files) are skipped.
    """
    findings: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts or path.name in excluded:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        labels: list[str] = []
        if _FORBIDDEN_IMPORT_RE.search(text):
            labels.append("forbidden-import")
        if _CLINICAL_MARKER_RE.search(text):
            labels.append("clinical-surface")
        if _DISPLAY_MARKER_RE.search(text):
            labels.append("display-surface")
        if _PRODUCTION_IMPORT_RE.search(text):
            labels.append("production-import")
        if _CREDENTIAL_MIGRATION_RE.search(text):
            labels.append("credential-migration")
        if labels:
            findings.append(f"{path.relative_to(root)}:{','.join(sorted(set(labels)))}")
    return tuple(findings)


def scan_migration_versions(versions_dir: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Revision ids and single-head check over the Alembic versions dir."""
    revisions: list[str] = []
    for path in sorted(versions_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = _REVISION_RE.search(text)
        if match:
            revisions.append(match.group(1))
    children: dict[str, int] = {}
    for revision in revisions:
        children[revision] = 0
    down_revisions: list[str] = []
    for path in sorted(versions_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r'down_revision\s*=\s*["\']([^"\']+)["\']', text)
        if match:
            down_revisions.append(match.group(1))
    heads = [r for r in revisions if r not in down_revisions]
    return tuple(sorted(revisions)), tuple(sorted(heads))


def run_guardrails(repo_root: Path) -> GuardrailReport:
    """Evaluate all frozen negative-boundary guards on the current tree."""
    backend = repo_root / "apps/backend"
    src_root = backend / "src"
    tests_root = backend / "tests"
    phase2_root = src_root / "hfm" / "phase2"

    hfb_findings = list(scan_hfb_coupling(src_root)) + list(scan_hfb_coupling(tests_root))

    marker_findings: list[str] = []
    if phase2_root.is_dir():
        marker_findings.extend(scan_forbidden_markers(phase2_root, excluded=_VERIFIER_FILES))

    revisions: tuple[str, ...] = ()
    heads: tuple[str, ...] = ()
    versions_dir = backend / "alembic" / "versions"
    if versions_dir.is_dir():
        revisions, heads = scan_migration_versions(versions_dir)

    adr_violations = tuple(sorted(wp for wp, adr in ADR_GATES.items() if adr not in ACCEPTED_ADRS))

    return GuardrailReport(
        clinical=CLINICAL_STATE,
        ai=AI_STATE,
        display=DISPLAY_STATE,
        xr=XR_STATE,
        credential_migration=CREDENTIAL_MIGRATION_STATE,
        production_hfb_import=PRODUCTION_HFB_IMPORT_STATE,
        m4_m7=M4_M7_STATE,
        accepted_adrs=ACCEPTED_ADRS,
        adr_gates=ADR_GATES,
        adr_gate_violations=adr_violations,
        hfb_coupling_findings=tuple(sorted(set(hfb_findings))),
        forbidden_marker_findings=tuple(sorted(set(marker_findings))),
        migration_revisions=revisions,
        migration_heads=heads,
    )
