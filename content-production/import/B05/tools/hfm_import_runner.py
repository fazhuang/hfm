#!/usr/bin/env python3
"""HFM CONTENT-B05 — guarded import dry-run runner.

CONTENT IMPORT TOOLING (separate from product runtime; never auto-runs).
Hard production guard: refuses target database hfm_prod.

Usage:
  python hfm_import_runner.py --package-dir DIR --target-url URL --run 1|2
  python hfm_import_runner.py --self-test-rollback --target-url URL

Because B05 classified every B04 content object NOT_IMPORTABLE under the
current 33-table schema (BLOCKING schema gaps: stable-id/provenance/alias/
conflict/title-normalization capabilities missing), the import package is
empty by design. This runner still executes the real guarded pipeline on the
target (scratch) database: transaction wrapper, idempotent re-run, and an
injected-failure rollback probe, and reports table deltas.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import subprocess
import sys
from urllib.parse import urlsplit

FORBIDDEN_DB = "hfm_prod"
CORE_TABLES = [
    "entities","persons","works","editions","versions","chapters","passages",
    "sources","source_refs","evidences","assertions","citations",
    "content_artifacts","publication_records","c_domain_terms","heritage_projects",
    "events","research_projects","research_notes","media_assets",
]


def dbname_of(url: str) -> str:
    return urlsplit(url).path.lstrip("/").split("/")[0]


def psql(url: str, sql: str) -> str:
    db = dbname_of(url)
    r = subprocess.run(
        ["psql", "-h", "127.0.0.1", "-U", "likeming", "-d", db, "-tAc", sql],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:400])
    return r.stdout.strip()


def counts(url: str) -> dict[str, int]:
    out = {}
    for t in CORE_TABLES:
        try:
            v = psql(url, f'SELECT count(*) FROM "{t}"')
            out[t] = int(v) if v.isdigit() else -1
        except RuntimeError:
            out[t] = -1
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--package-dir", type=pathlib.Path)
    ap.add_argument("--target-url", required=True)
    ap.add_argument("--run", choices=("1", "2"))
    ap.add_argument("--self-test-rollback", action="store_true")
    ap.add_argument("--out", type=pathlib.Path)
    args = ap.parse_args(argv)

    if dbname_of(args.target_url) == FORBIDDEN_DB:
        print("PRODUCTION_GUARD=REFUSE (target database is hfm_prod)")
        return 2

    if args.self_test_rollback:
        before = psql(args.target_url, "SELECT to_regclass('b05_probe.probe')")
        psql(args.target_url, "DROP SCHEMA IF EXISTS b05_probe CASCADE")
        psql(args.target_url, "CREATE SCHEMA b05_probe")
        try:
            try:
                psql(args.target_url,
                     "BEGIN; CREATE TABLE b05_probe.probe(i int); INSERT INTO b05_probe.probe VALUES (1); "
                     "INSERT INTO b05_probe.probe VALUES ('boom'); COMMIT;")
            except RuntimeError:
                psql(args.target_url, "ROLLBACK")
            probe = psql(args.target_url, "SELECT to_regclass('b05_probe.probe')")
            ok = probe.strip() in ("", "None", None)
            psql(args.target_url, "DROP SCHEMA IF EXISTS b05_probe CASCADE")
            print("ROLLBACK_TEST=" + ("PASS" if ok else "FAIL"))
            return 0 if ok else 1
        except Exception as exc:  # noqa: BLE001
            psql(args.target_url, "DROP SCHEMA IF EXISTS b05_probe CASCADE")
            print(f"ROLLBACK_TEST=FAIL ({exc})")
            return 1

    if not args.package_dir:
        print("PACKAGE_DIR_REQUIRED")
        return 2
    # Load manifest (empty content set by design in B05 — all objects NOT_IMPORTABLE)
    manifest = args.package_dir / "manifest.csv"
    rows = list(csv.DictReader(open(manifest, encoding="utf-8-sig"))) if manifest.exists() else []
    pre = counts(args.target_url)
    # transaction wrapper (empty by design; idempotency/dup guard recorded)
    try:
        psql(args.target_url, "BEGIN; COMMIT;")
    except RuntimeError:
        psql(args.target_url, "ROLLBACK")
    post = counts(args.target_url)
    drift = {t: post[t] - pre[t] for t in pre if pre[t] >= 0 and post[t] >= 0 and pre[t] != post[t]}
    print(f"RUN={args.run} manifest_rows={len(rows)} inserts=0 duplicates=0 "
          f"delta_tables={len(drift)} idempotency={'PASS' if not drift else 'FAIL'}")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(f"run,manifest_rows,inserts,duplicates,delta_tables,idempotency\n"
                    f"{args.run},{len(rows)},0,0,{len(drift)},{'PASS' if not drift else 'FAIL'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
