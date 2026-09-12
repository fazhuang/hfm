# HFM Phase 2 — P2-07 E2-22 Restore Drill Evidence

Status: FORMAL TRACKED EVIDENCE · P2-07 (Frontier-2) · machine-executed
Evidence ID: **E2-22**
WP: **P2-07** (Deployment / Operations Foundation)
AC: **P2-07-AC-04** — "Backup/restore verified on the test environment" (negative: no untested restore)
Frozen Evidence Contract row: `| E2-22 | P2-07 | P2-07-AC-04 | backup/restore drill log | run restore drill on test env | restore verified |`

## Execution record (actual machine run, 2026-08-31T00:09:52Z)

Procedure: `scripts/backup-restore.sh` (P2-07 runbook) — real backup of the isolated
local test fixture database, then real restore into an isolated target with integrity
and marker validation. No production action; no external destructive action; no
credential exposure.

```text
$ ./scripts/backup-restore.sh backup test
BACKUP_ARTIFACT=/Users/likeming/Sites/hfm/infra/backups/hfm-test-1788134992.db

$ shasum -a 256 infra/backups/hfm-test-1788134992.db
8ac0bfffb70640e4a33bd608e7525ae2edf8ad34228630b0035f7d4d5e573f64

$ ./scripts/backup-restore.sh restore test hfm-test-1788134992.db --verify
RESTORE_DRILL=PASS (restored target=.../infra/backups/restored-test.db,
integrity=ok, tables=['demo_items'], marker=restore-drill-item)
```

## Validation

- Execution result: **PASS** (exit 0)
- Integrity validation: **PASS** (`PRAGMA integrity_check` = ok on the restored target)
- Marker validation: **PASS** (fixture row `id='a1', title='restore-drill-item'` present)
- Schema validation: **PASS** (`demo_items` table present in restored target)
- Backup artifact hash: `8ac0bfffb70640e4a33bd608e7525ae2edf8ad34228630b0035f7d4d5e573f64` (SHA-256)
- Failure path (contract requires): corrupt backup → `RESTORE_VERIFY=FAIL`, exit non-zero
  (established previously by the P2-07 restore-drill failure semantics)

## Cleanup

Transient execution artifacts (`infra/backups/restored-test.db`, `fixture.db`,
`hfm-test-*.db`) are temporary and removed after execution; the `infra/backups/`
directory is gitignored (`*.dump`) and holds no tracked backup content. This
document is the formal tracked evidence artifact.

## Candidate binding

- Original Frontier-2 candidate: `d38f871a230ca56713737b7de82f9111e7e73650`
- Evidence executed and recorded under the current Phase-2 Governance Baseline:
  `7fa7c4f60244daa6999e377d08502bde522c56b2`
- Bound by this evidence artifact to P2-07-AC-04 / E2-22.
