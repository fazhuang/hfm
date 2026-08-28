# HFM NPG-0 — Phase 0.4 Baseline Integrity Audit

Date: 2026-08-29
Mode: READ-ONLY FACT AUDIT; report artifact only
Target baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`

## 1. Result

**BLOCK**

The named commit is a valid, complete Git parent baseline and is the current `main`/`origin/main` commit, but the live working tree is not clean. A tracked Phase 0.4 CORE-COMPLETION file has an uncommitted change. No file was changed, restored, checked out, imported, or repaired by this audit.

## 2. Repository binding

| Fact | Evidence | Result |
| --- | --- | --- |
| Audit repository | `/Users/likeming/Sites/hfm` | CONFIRMED |
| Branch | `main`, upstream `origin/main` | CONFIRMED |
| HEAD | `0167b1702dac13993a5206f63752eafcc8e5387e` | CONFIRMED |
| origin/main | `0167b1702dac13993a5206f63752eafcc8e5387e` | CONFIRMED |
| HEAD vs origin/main | ahead 0 / behind 0 | CONFIRMED |
| Commit object | `git cat-file -t 0167…` → `commit` | CONFIRMED |
| Baseline tree | `a9b21b083a6cd63486a1d1cf94d33dd7daecf984` | CONFIRMED |
| Commit checkoutability | Commit resolves, `main` contains it, and `git archive 0167…` materialized its tree in `/private/tmp` | CONFIRMED WITHOUT CHECKOUT |
| Tags | No tag contains the baseline | NONE |
| Branches containing baseline | local `main`; remote `origin/main` | CONFIRMED |
| Commits after baseline on any ref | `git log 0167….. --all` returned none | NONE |

## 3. Working tree integrity

Audit-start status:

```text
## main...origin/main
 M scripts/core_completion/dry_run.py
```

Tracked diff: 23 lines (`18 insertions`, `5 deletions`), formatting-only by inspection. The live blob is `ffb988789b86ea3eb07546d640125c163d7e0237`; the frozen baseline blob is `06c5c3755360b52090af79b56c0584b0f8c844da`.

Semantic impact is not the acceptance rule: the working tree is dirty and the changed file is part of the frozen CORE-COMPLETION implementation/evidence path. Therefore the live checkout cannot be certified as an untouched Next-Phase parent working tree.

## 4. Baseline lineage

All named HFM objects resolve as commits, and every ancestor check returned exit code `0`:

```text
366df69715613022326eb7a3c06ae7f145ebacb9  Original contract
  → 00ed3ff244578d975c2748fa9d85a8d14e4c7c37  Amended contract
  → d08e343dbbc52dedfcbd5bba69918e6a4b74256d  CD-6 implementation baseline
  → 7960fb64a43250573d436898d45c7aa615bff1f6  Accepted CORE-COMPLETION candidate
  → 0167b1702dac13993a5206f63752eafcc8e5387e  Phase 0.4 archive/freeze baseline
```

The only committed delta from candidate `7960fb64` to completion baseline `0167b170` is:

```text
M README.md
A docs/audit/HFM-PHASE0.4-CORE-COMPLETION-ACCEPTANCE-ARCHIVE.md
M docs/governance/BASELINE-MANAGEMENT.md
```

This is consistent with a governance-only archive/freeze event.

## 5. Frozen evidence integrity

The eight original v0.1 frozen contract artifacts have identical Git blob IDs at `366df697` and `0167b170`:

- `docs/domain/HFM-CORE-DOMAIN-SCOPE-v0.1.md`
- `docs/domain/HFM-CANONICAL-DOMAIN-MODEL-v0.1.md`
- `docs/domain/HFM-ASSERTION-CONTRACT-v0.1.md`
- `docs/domain/HFM-EVIDENCE-LINEAGE-CONTRACT-v0.1.md`
- `docs/migration/hfb/HFM-PHASE0.4-CORE-ASSET-INVENTORY.md`
- `docs/migration/hfb/HFM-PHASE0.4-CORE-MIGRATION-DAG.md`
- `docs/migration/hfb/HFM-CORE-DATA-MIGRATION-STRATEGY-v0.1.md`
- `docs/governance/HFM-CORE-DOMAIN-DEFINITION-OF-DONE.md`

At `0167b170`, the governing records state:

| Record | Baseline fact |
| --- | --- |
| `BASELINE-MANAGEMENT.md` | Phase 0.4 `COMPLETE / ACCEPTED / ARCHIVED / FROZEN`; inventory 28/28; DoD 9/9; production import NO; CD-7 nonexistent; Phase 1 separately authorized only |
| Amendment v0.2 | 28/28 dispositions; CORE-COMPLETION is a non-CD dry-run owner; CD-7 nonexistent; Phase 1 not authorized |
| Core inventory | CA-001…CA-028 present |
| Completion evidence | Frozen inventory 28/28 preserved; persistent production state none; production records imported 0 |
| Acceptance archive | Candidate `7960fb64` accepted; candidate explicitly differs from completion baseline; final verdict PASS |
| DoD | Nine obligations enumerated; completion archive records 9/9 PASS/CLOSED |
| Machine artifact | Governance `00ed3ff`, implementation `d08e343`, source `03755b57`, production DB touched `false` |

Documentation ambiguity: `README.md:43` describes the completion baseline as “`d08e343…链上最新归档冻结提交`”, while `BASELINE-MANAGEMENT.md` and the archive correctly use the self-referential archive commit. This is a P1 selection risk, not evidence that `d08e343` is the final baseline.

## 6. Required answers

| Question | Answer | Evidence |
| --- | --- | --- |
| A. 当前工作树是否 clean？ | **NO** | One tracked modification in `scripts/core_completion/dry_run.py` |
| B. `0167b170` 是否存在且可 checkout？ | **YES** | Commit object resolves; branch points to it; tree exported successfully. Checkout intentionally not performed |
| C. 冻结文件其后是否发生未授权变化？ | **YES IN LIVE WORKTREE; NO COMMITTED POST-BASELINE CHANGE** | Uncommitted CORE-COMPLETION script drift; no commit after baseline |
| D. `7960fb64` 是否正确保留为 candidate？ | **YES** | Archive §§3, 20–21: accepted candidate ≠ archive/freeze baseline |
| E. 是否存在 CD-7？ | **NO / NONEXISTENT** | DAG stops at CD-6; amendment and archive state NONEXISTENT |
| F. 是否存在 Production HFB Import 实际执行证据？ | **NO** | Evidence says 0 imported records, persistent state NONE, production DB touched false. Production environment was not probed |
| G. Phase 1 是否已提前实现？ | **NO COMMIT OR PRODUCT IMPLEMENTATION FOUND** | No post-baseline commit; baseline APIs are health/system only; frontend has one skeleton route; Phase 1 mentions are documents/placeholders |

## 7. Fresh baseline verification

The baseline commit was exported from the Git object to `/private/tmp/hfm-npg-0167.HAqWDA`; checks ran there, not against the dirty checkout:

| Check | Exit | Result |
| --- | ---: | --- |
| Backend `pytest -q` | 0 | PASS; 235 tests by progress count; one existing Starlette/httpx deprecation warning |
| Backend `ruff check src tests` | 0 | PASS |
| Backend `mypy --strict src tests` | 0 | PASS; 101 source files |
| Frontend `npm run lint` | 0 | PASS |
| Frontend `npm run typecheck` | 0 | PASS |
| Frontend `npm run test` | 0 | PASS; 8 files / 24 tests |
| Frontend `npm run build` | 0 | PASS; 30 modules transformed |

These checks prove the Git baseline builds and tests in the available local environment. They do not convert the live dirty checkout into a clean parent and do not prove a production import or production deployment.

## 8. Blocker

**P0-NPG0-01 — DIRTY FROZEN WORKTREE:** the only formal next-phase parent commit is valid, but the live checkout contains uncommitted drift in a Phase 0.4 CORE-COMPLETION file. Scope arbitration must bind to the Git object or begin from a separately confirmed clean checkout; this audit performs neither cleanup nor checkout.

## 9. Final verdict

**BLOCK**
