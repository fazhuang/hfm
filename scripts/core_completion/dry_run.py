#!/usr/bin/env python3
"""HFM Phase 0.4 CORE-COMPLETION — data migration dry-run runner.

Executes the frozen dry-run (Migration Strategy §4: extract → validate →
transform → dry-run → reconciliation) against the frozen HFB snapshot
`03755b5` tracked source artifact, in an isolated/disposable environment:

  - source: apps/frontend/src/data/huangfu_mi_exhibition.json @ 03755b5
    (sha256-verified against the frozen value; no HFB current HEAD, no
    mutable working data)
  - target: disposable temporary SQLite database (deleted on exit;
    persistent state after dry-run = NONE)
  - Run A + Run B (reproducibility) + idempotency re-run
  - fail-closed: any exception exits non-zero with error evidence

Usage:
  python3 scripts/core_completion/dry_run.py \
      [--hfb <path-to-hfb-snapshot-checkout>] [--out-dir <dir>]
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

_HFM_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _HFM_ROOT / "apps" / "backend" / "src"
sys.path.insert(0, str(_BACKEND_SRC))

from hfm.completion.migration import (  # noqa: E402
    MIGRATION_VERSION,
    RunResult,
    extract_source,
    reconciliation_manifest,
    run_dry_run,
)
from hfm.core.hashing import calculate_canonical_metadata_sha256  # noqa: E402

#: Frozen expected source digest (verified against snapshot 03755b5).
EXPECTED_SOURCE_SHA256 = "94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb"
SOURCE_RELPATH = "apps/frontend/src/data/huangfu_mi_exhibition.json"

#: Normalized evidence comparison keys (volatile fields excluded — §21).
COMPARISON_KEYS = (
    "reconciliation",
    "total",
    "rejections",
    "duplicates",
    "candidate_set_sha256",
    "target_candidate_count",
)


def load_source_records(source: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    try:
        data = json.loads(source["raw"])
    except json.JSONDecodeError as exc:
        raise ValueError(f"frozen source artifact is not valid JSON: {exc}") from exc
    exhibition = data["exhibition"]
    persons = [exhibition["person_overview"]]
    editions = data["classical_editions"]
    # C3: no citation-shaped records are tracked in the frozen snapshot
    # (untracked hfb_dev.db is excluded by source-integrity rule) — the
    # transformation rule is exercised by unit tests with representative
    # polymorphic-target records.
    citations: list[dict] = []
    return persons, editions, citations


def write_target_candidates(result: RunResult) -> tuple[str, int]:
    """Apply candidate rows to a disposable SQLite target (isolation §13).

    Returns (db_path, row_count); the caller deletes the file afterwards.
    """
    fd, db_path = tempfile.mkstemp(suffix=".db", prefix="hfm-core-completion-")
    os.close(fd)
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "CREATE TABLE candidates ("
            "class_id TEXT NOT NULL, kind TEXT NOT NULL,"
            "candidate_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        con.executemany(
            "INSERT OR IGNORE INTO candidates (class_id, kind, candidate_id, payload)"
            " VALUES (?, ?, ?, ?)",
            [
                (c.class_id, c.kind, c.candidate_id, json.dumps(c.payload, ensure_ascii=False))
                for c in result.candidates
            ],
        )
        con.commit()
        rows = con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        return db_path, int(rows)
    finally:
        con.close()


def execute_one(source: dict[str, Any], persons, editions, citations) -> RunResult:
    result = run_dry_run(source, persons, editions, citations)
    db_path, rows = write_target_candidates(result)
    result.target_db_rows = rows
    try:
        os.unlink(db_path)  # disposable target — persistent state after dry-run: NONE
    except OSError as exc:
        result.errors.append(f"disposable target cleanup failed: {exc}")
    return result


def normalized_evidence(result: RunResult) -> dict:
    manifest = reconciliation_manifest(result)
    return {key: manifest[key] for key in COMPARISON_KEYS}


def main() -> int:
    parser = argparse.ArgumentParser(description="HFM Phase 0.4 CORE-COMPLETION dry-run")
    parser.add_argument("--hfb", default="/Users/likeming/Sites/hfb", help="HFB snapshot checkout")
    parser.add_argument("--out-dir", default=str(_HFM_ROOT / "artifacts" / "audit"))
    args = parser.parse_args()

    source_path = Path(args.hfb) / SOURCE_RELPATH
    if not source_path.exists():
        print(f"FATAL: frozen source artifact not found: {source_path}", file=sys.stderr)
        return 2

    source = extract_source(str(source_path))
    if source["sha256"] != EXPECTED_SOURCE_SHA256:
        print(
            f"FATAL: source digest mismatch: expected {EXPECTED_SOURCE_SHA256} "
            f"got {source['sha256']}",
            file=sys.stderr,
        )
        return 2

    persons, editions, citations = load_source_records(source)
    print(f"source: {source_path} sha256={source['sha256'][:16]}…")
    print(
        f"source records: persons={len(persons)} editions={len(editions)} "
        f"citations={len(citations)}"
    )

    # Run A + Run B (reproducibility)
    run_a = execute_one(source, persons, editions, citations)
    run_b = execute_one(source, persons, editions, citations)

    ev_a = normalized_evidence(run_a)
    ev_b = normalized_evidence(run_b)
    reproducibility = ev_a == ev_b

    # Idempotency: fresh re-run yields the identical candidate id set
    rerun = execute_one(source, persons, editions, citations)
    ids_a = sorted(c.candidate_id for c in run_a.candidates)
    ids_rerun = sorted(c.candidate_id for c in rerun.candidates)
    idempotent = ids_a == ids_rerun and len(ids_a) == run_a.total.target

    # Disposable target rows prove the insert path with no persistent state
    evidence = {
        "governance_baseline": "00ed3ff244578d975c2748fa9d85a8d14e4c7c37",
        "implementation_baseline": "d08e343dbbc52dedfcbd5bba69918e6a4b74256d",
        "source_baseline": "03755b57ec0e4c8023d1447619f7d6ead9e44d73",
        "source_artifact": SOURCE_RELPATH,
        "source_sha256": source["sha256"],
        "source_records": {
            "persons": len(persons),
            "editions": len(editions),
            "citations": len(citations),
        },
        "migration_version": MIGRATION_VERSION,
        "run_a": {
            "reconciliation": run_a.total.as_dict(),
            "rejections": run_a.rejections,
            "duplicates": run_a.duplicates,
            "candidate_set_sha256": run_a.candidate_set_sha256,
            "target_db_rows": run_a.target_db_rows,
        },
        "run_b": {
            "reconciliation": run_b.total.as_dict(),
            "rejections": run_b.rejections,
            "duplicates": run_b.duplicates,
            "candidate_set_sha256": run_b.candidate_set_sha256,
            "target_db_rows": run_b.target_db_rows,
        },
        "reconciliation_schema": [
            "source",
            "accepted",
            "transformed",
            "rejected",
            "duplicate",
            "target",
        ],
        "equations": {
            "source_eq": "source = accepted + rejected + duplicate",
            "accepted_eq": "accepted = transformed",
            "target_eq": "target = transformed - duplicate_consumed",
        },
        "reproducibility": {
            "result": "PASS" if reproducibility else "FAIL",
            "run_a_eq_run_b": reproducibility,
            "normalized_keys": list(COMPARISON_KEYS),
            "excluded_volatile_fields": ["timestamps", "temp db paths", "run ids"],
        },
        "idempotency": {
            "result": "PASS" if idempotent else "FAIL",
            "candidate_id_set_stable": idempotent,
            "rerun_target_count": rerun.total.target,
        },
        "isolation": {
            "mode": "disposable temporary SQLite (tempfile, deleted after run)",
            "persistent_state_after_dry_run": "NONE",
            "production_db_touched": False,
        },
        "errors": run_a.errors + run_b.errors + rerun.errors,
        "silent_failure_paths": 0,
    }
    # per-class reconciliation
    evidence["reconciliation_by_class"] = {
        cls: rc.as_dict() for cls, rc in sorted(run_a.reconciliation.items())
    }
    evidence["candidate_set_manifest_sha256"] = calculate_canonical_metadata_sha256(
        {"run_a": ev_a["candidate_set_sha256"], "run_b": ev_b["candidate_set_sha256"]}
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "hfm-phase0.4-core-completion.json"
    out_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"total": run_a.total.as_dict()}, ensure_ascii=False))
    print(f"reproducibility: {'PASS' if reproducibility else 'FAIL'}")
    print(f"idempotency: {'PASS' if idempotent else 'FAIL'}")
    print(f"evidence: {out_path}")
    return 0 if (reproducibility and idempotent and not evidence["errors"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
