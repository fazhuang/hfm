# WORKSPACE-GOVERNANCE-REMEDIATION-REPORT (WG-03)

GENERATED_AT: 2026-09-10
TASK: HFM Main Worktree Governance Remediation (WG-03)
NATURE: controlled execution attempt — **halted before any mutation**
PRE-REMEDIATION_INVENTORY: `WG03-PRE-REMEDIATION-INVENTORY.txt`

## 1. Reality snapshot (verified before any action)

```
PWD=/Users/likeming/Sites/hfm
REPO_TOPLEVEL=/Users/likeming/Sites/hfm
BRANCH=hfm-canonical
HEAD=92f206c85ddbc4a6403c2c323de063aa665ecde3   (== required baseline)  PASS
TRACKED_DIRTY=0
UNTRACKED_TOTAL=4021
SOURCE_UNTRACKED_TOTAL=4019  (= 4021 − 2 WG governance docs: WORKSPACE-GOVERNANCE-ACTION-PLAN.md,
                              WORKSPACE-GOVERNANCE-UNTRACKED-DIAGNOSTIC.md; WG-01 excluded its own diagnostic)
WORKTREE_STATUS=clean (tracked) with 4021 untracked paths
NOTE: this round additionally produced 2 WG-03 governance artifacts
      (`WG03-PRE-REMEDIATION-INVENTORY.txt`, `WORKSPACE-GOVERNANCE-REMEDIATION-REPORT.md`),
      so the post-round untracked total is 4023 (4019 frozen + 2 WG docs + 2 WG-03 artifacts).
```

Governance artifacts found: `WORKSPACE-GOVERNANCE-ACTION-PLAN.md` (WG-02, embeds the manifests),
`WORKSPACE-GOVERNANCE-UNTRACKED-DIAGNOSTIC.md`. No separate WG-02 manifest files exist.

## 2. Manifest reconciliation (measured, before execution)

| Bucket | Frozen | Measured | Result |
| --- | ---: | ---: | --- |
| TRACK_MANIFEST (§7.1, itemized list) | 79 | 79 listed, **79/79 present & untracked** | **exact** |
| MOVE_ARCHIVE (§7.3, whole `video-production/`) | 2955 | 2955 untracked under `video-production/` | **exact** |
| DELETE_REGENERABLE (§7.4, category description) | 985 | plan components sum to **975**; residual untracked set = 985 | **FAIL — inconsistent** |
| Governance docs | n/a | 2 | accounted |

Residual (= the frozen 985 delete bucket, by subtraction: 4021 − 79 − 2955 − 2 = 985) decomposes as:
`458 corpus/extracted-text` · `392 corpus/raw-ocr` · `113 batches/*` · `8 corpus/work` ·
`3 oddly-quoted B01/person/extracted-text` · `1 .playwright-cli` ·
**`9 content-production/import/B05/*`** · **`1 content-production/import/pwe-tooling/PWE-IT-02-R1-CODEX-REACCEPTANCE.md`**.

### Blocker evidence — the frozen DELETE bucket contains formal, non-regenerable assets

```
content-production/import/B05/package/documents.csv          ← the frozen 675-row import input (SHA 27bccdd6…)
content-production/import/B05/package/manifest.csv
content-production/import/B05/csv-database-map.csv
content-production/import/B05/expected-database-delta.csv
content-production/import/B05/identity-policy-check.csv
content-production/import/B05/page-output-identity-policy.csv
content-production/import/B05/reconciliation.csv
content-production/import/B05/schema-gaps.csv
content-production/import/B05/validation-report.csv
content-production/import/pwe-tooling/PWE-IT-02-R1-CODEX-REACCEPTANCE.md   ← governance acceptance artifact
```

Plan §7.4 also mismatches the filesystem on category counts:
`corpus/work 10→8` · `B01/jiayi/raw-ocr 7→8` · `B01/jiayi/rendered-pages 13→14` ·
`B02 "92 json+images" → 65 residual` · `.playwright-cli 1→1 (dir has 2 entries)`.

## 3. Why execution was halted (protocol-correct, no scope expansion)

- The frozen `DELETE_REGENERABLE_MANIFEST` is **not an itemized path list**; it is a category description whose own
  components total **975 ≠ 985**, and its per-category counts disagree with the current filesystem.
- Deleting "by the plan categories" would leave ≥10 formal assets untracked (untracked ≠ 0 → §10 fails).
- Deleting "by the residual set" would **destroy formal governance assets that are not in Git**
  (including the frozen import package `B05/package/documents.csv`) — forbidden by §七 (protect formal assets)
  and by the no-unrelated-files/no-reclassification rules.
- Per §五 (no broad directory deletion instead of a manifest) and §十四 (STOP on manifest reconciliation failure),
  no `git add`, no `mv`, no `rm`, no `.gitignore` change was performed.

Nothing was mutated: HEAD remains `92f206c…`, tracked worktree unchanged, untracked_total unchanged.

## 4. Not performed (blocked)

`TRACK staging/commit` · `video-production → /Users/likeming/Sites/hfm-video-production move` ·
`git init` of the video workspace · `985-file deletion` · `.gitignore` update · governance commit.
`/Users/likeming/Sites/hfm-video-production` was confirmed **absent** (no target conflict).

## 5. Read-only confirmations

```
PWE_BASELINE_INTEGRITY=PASS   (see §6 — tracked & unmodified)
MAPPING_BASELINE_ID=077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b
hfm_prod: documents=675 entities=0 persons=0 works=0 editions=0
HFM_PROD_WRITE_EXECUTED=NO
```

## 6. Required output block (§十三)

```text
WG03_STATUS=FAIL

SOURCE_UNTRACKED_TOTAL=4019

TRACK_EXPECTED=79
TRACK_RECONCILIATION=PASS

VIDEO_MOVE_EXPECTED=2955
VIDEO_MOVE_ACTUAL=0
VIDEO_MOVE_RECONCILIATION=FAIL

DELETE_EXPECTED=985
DELETE_ACTUAL=0
DELETE_RECONCILIATION=FAIL

VIDEO_WORKSPACE_SOURCE_REMOVED=NO
VIDEO_WORKSPACE_TARGET=
VIDEO_INDEPENDENT_GIT_REPO=NO

GITIGNORE_UPDATED=NO
IGNORE_RULE_VALIDATION=NOT_RUN

SECRET_CHECK=NOT_RUN (no commit attempted)

PWE_BASELINE_INTEGRITY=PASS
MAPPING_BASELINE_ID=077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b

PRE_GOVERNANCE_HEAD=92f206c85ddbc4a6403c2c323de063aa665ecde3
GOVERNANCE_COMMIT= (none)
POST_GOVERNANCE_HEAD=92f206c85ddbc4a6403c2c323de063aa665ecde3
ANCESTRY=PASS (unchanged)
AUTHORIZED_DIFF_ONLY=NOT_RUN (no commit)

WORKTREE_CLEAN=NO (4021 untracked paths remain)
UNTRACKED_COUNT=4021
MODIFIED_COUNT=0

PWE_TOOLING_TESTS=NOT_RUN (no code change this round)
RELEVANT_BACKEND_TESTS=NOT_RUN (no code change this round)

HFM_PROD_WRITE_EXECUTED=NO

READY_FOR_PWE_IT02_R2_REACCEPTANCE=NO

BLOCKER=DELETE_REGENERABLE_MANIFEST_NOT_ITEMIZED_AND_INCONSISTENT:
        frozen §7.4 components sum 975 != 985; per-category counts mismatch the filesystem; and the 985 residual
        therefore contains >=10 non-regenerable formal assets (B05 import package/reports, PWE Codex acceptance).
        Executing either the plan categories or the residual set would violate §五/§七 and §十, and
        §十四 mandates STOP on manifest reconciliation failure.
STOP=YES
```

## 7. Recommended next gate

Re-issue WG-02 as an **itemized, per-path** DELETE manifest (985 explicit repo-relative paths) with a corrected,
reconciled TRACK/MOVE/DELETE accounting that excludes formal assets (at minimum the 10 listed above, which should
move to TRACK or KEEP), then re-run WG-03 under the same authorization. No remediation action should be taken
from the current WG-02 description as-is.
