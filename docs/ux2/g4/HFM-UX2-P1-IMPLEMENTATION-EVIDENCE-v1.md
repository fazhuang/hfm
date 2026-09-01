# HFM-UX2-P1 Implementation Evidence v1 (Corrective)

Status: UX2-P1 CORRECTED IMPLEMENTATION CANDIDATE · ready for independent
re-audit (rejected candidate `7f603d385e258e62afab7dca6eba5210ed8a2d68` superseded)

## 1. WP Identity

```text
WP = UX2-P1 · Person Archive
PRE_WP_BASELINE = 2b315795e43faf92e03cd3db2c74b18c47c0927e
REJECTED_CANDIDATE = 7f603d385e258e62afab7dca6eba5210ed8a2d68 (preserved in history)
CORRECTIVE_BASIS = rejected candidate (linear successor; no amend/squash)
```

## 2. Corrective Scope (audited findings)

| Finding | Disposition | Correction |
| --- | --- | --- |
| P0-01 worktree identity gate | CLOSED | Untracked `docs/research/ hfmzl/ zzcl/` classified as unrelated pre-existing user/project material (present since before UX2; customer source archives + research notes, intentionally untracked). Isolated via local `.git/info/exclude` — no deletion, no commit, worktree now CLEAN. |
| P0-02 晋书 evidence aggregation | CLOSED | Evidence label no longer aggregates the 12 论其人 citations under 《晋书》房玄龄等. The 12 citations are heterogeneous (房玄龄等 ×3, 司马炎, 李巨来, 钱熙祚, 张发荣, 后世综合评价 ×3, 国际影响, 晋书轶事). Label is now the mechanically derived generic statement `后论 · 论其人（历代评价引文 12 条 · 出处逐条标注）`; per-citation provenance lives in the reader document. |
| P1-01 archival media proof | CLOSED | Media projection bound to the authoritative `archiveInventory.ts a-movies` record (客户提供：皇甫谧电影资料; 《皇甫谧一》《针灸鼻祖皇甫谧》第 1 集 大器晚成; `INVENTORY_MOVIES = 2`). Unit + e2e fixtures are deterministic projections of that record with in-test binding assertions; no synthetic acceptance fixture. |
| P1-02 browser acceptance | CLOSED | Real-browser e2e: reader navigation (其传 → back → 后论, real content, no dead routes), keyboard/focus (Tab reach, Enter activate, visible focus ring, no trap), browser-level axe = 0, responsive 375/1280/1920 no overflow. |
| P2-01 candidate SHA placeholder | OPEN_DOCUMENTATION_ONLY — CLOSE_AT_UX2_P1_ACCEPTANCE_ARCHIVE | Not attempted (self-referential SHA impossible); acceptance archive will replace placeholder. |
| P2-02 evidence accuracy | CLOSED | Actual reproduced numbers recorded below (ESLINT 0 errors / 965 warnings as actually reproduced; WORKTREE=CLEAN verified after local isolation). |

## 3. Changed Paths (corrective delta vs rejected candidate)

| Path | Change |
| --- | --- |
| `apps/frontend/src/views/persons/PersonDetailView.vue` | P0-02: generic 后论 citation aggregate (no 《晋书》 misattribution) |
| `apps/frontend/src/__tests__/ux2_p1_person.spec.ts` | P0-02 fail-on-defective provenance assertions; P1-01 real-media binding + proof tests |
| `apps/frontend/e2e/ux2-p1-person.spec.ts` | P1-01 real media projection; P1-02 reader nav / keyboard / browser axe / responsive |
| `docs/ux2/g4/HFM-UX2-P1-IMPLEMENTATION-EVIDENCE-v1.md` | this record (P2-02 accuracy) |
| `.git/info/exclude` | P0-01 local isolation (NOT a tracked file; not committed) |

## 4. Acceptance Criteria (frozen WP DAG DoD)

| Criterion | Result |
| --- | --- |
| DHObjectLayout regions + states on person page | PASS |
| heading order correct | PASS (single H1, no skips) |
| F-5 sections from real data | PASS (Life Events timeline; Historical Assessments = houlun FULL_TEXT; Archival Media = a-movies-bound projection) |
| G1-C states | PASS (RESOURCE_READY / SCHOLARLY_UNCERTAIN / METADATA_ONLY / ABSENT_OPTIONAL) |
| Later Scholarship NOT added | PASS |
| PROVENANCE | PASS (P0-02: no aggregate attributed to a specific source) |

## 5. Test / Quality Results (independently reproduced)

```text
TARGETED_TESTS      = 17/17 PASS (ux2_p1_person.spec.ts)
P0_REGRESSION_TESTS = 58/58 PASS (ux2_p0_* — P0_REGRESSION = NONE)
FULL_VITEST         = 270/270 PASS (30 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_965_WARNINGS (actual reproduction; warnings are
                      the repo-wide pre-existing style-warning baseline, gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 72/72 PASS (67 existing + 5 corrective UX2-P1)
BROWSER_AXE         = 0 (real browser, full rule set)
P0_PRIMITIVE_DELTA  = ZERO (git diff 797e33f… HEAD -- primitives/presentation = empty)
```

## 6. Negative Boundaries

```text
NB-01 no historical fabrication   PASS   NB-02 no relation inference  PASS
NB-05 clinical                    PASS   NB-06 no citation synthesis  PASS
NB-07 missing ≠ absence           PASS   P0-02 provenance             PASS
```

## 7. Test-Quality Guarantee (fail-on-defective)

- P0-02: tests assert the 12-条 aggregate is NOT displayed with 《晋书》 attribution
  (`not.toMatch(/《晋书》[^（]*（[^）]*12[^）]*条）/`) — fails on the rejected label.
- P1-01: media fixture count + names must match the authoritative `a-movies`
  record (old single synthetic item fails the `INVENTORY_MOVIES = 2` binding).
- P1-02: reader navigation exercises real routes/content (dead routes fail);
  keyboard tests require Tab reachability + Enter activation (fail if
  keyboard-inaccessible); browser axe = 0 (fail on violations).

## 8. Worktree Status

```text
git status --short → CLEAN
(Local .git/info/exclude isolates pre-existing unrelated untracked material;
 no tracked production delta beyond the corrective files above.)
```

## 9. Rollback

```text
ROLLBACK_TARGET = 2b315795e43faf92e03cd3db2c74b18c47c0927e (PRE_WP_BASELINE)
```

## 10. Commit

```text
CORRECTED_UX2_P1_IMPLEMENTATION_CANDIDATE = <commit SHA recorded at delivery>
CANDIDATE_PARENT = 7f603d385e258e62afab7dca6eba5210ed8a2d68 (rejected candidate)
OUT_OF_SCOPE_CONFIRMED = YES (UX2-P2..P7 delta ZERO; P0 primitive delta ZERO)
```
