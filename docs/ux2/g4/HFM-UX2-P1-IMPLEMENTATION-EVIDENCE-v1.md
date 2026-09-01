# HFM-UX2-P1 Implementation Evidence v1 (Second Corrective)

Status: UX2-P1 CORRECTED_V3 IMPLEMENTATION CANDIDATE · ready for independent
re-audit (rejected V1 `7f603d385e258e62afab7dca6eba5210ed8a2d68`, rejected V2
`af337ebc00f210ce1ef331503e8a95ae25b701dd` superseded)

## 1. WP Identity

```text
WP = UX2-P1 · Person Archive
PRE_WP_BASELINE = 2b315795e43faf92e03cd3db2c74b18c47c0927e
REJECTED_V1 = 7f603d385e258e62afab7dca6eba5210ed8a2d68
REJECTED_V2 = af337ebc00f210ce1ef331503e8a95ae25b701dd
CORRECTIVE_BASIS = rejected V2 (linear successor; no amend/squash)
```

## 2. This Corrective Pass — P1-01 F-5 Archival Media Provenance Closure

Prior passes closed P0-01 / P0-02 / P1-02 / P2-02. This pass closes P1-01
only: the F-5 archival media acceptance proof now derives from the
AUTHORITATIVE per-media source instead of a test-authored fixture.

### MEDIA_SOURCE_OF_TRUTH

```text
hfmzl/皇甫谧/皇甫谧电影/
  皇甫谧一.mpg
  《针灸鼻祖皇甫谧》第1集 大器晚成.mpg
```

Tracked governance/domain records binding this source:

- `docs/design/HFM-CONTENT-ASSET-MAP.md` row 31 (filenames + count 2) and
  row 57 (license policy 授权公开（存在文件才可播放）)
- `apps/frontend/src/data/archiveInventory.ts` `a-movies` (sourceName
  客户提供：皇甫谧电影资料; description naming both movies; count
  `INVENTORY_MOVIES = 2`; status AVAILABLE)
- `apps/frontend/src/data/contentInventory.ts` `INVENTORY_MOVIES = 2`
- backend `phase2/media/models.py` defines the domain `MediaAsset` shape
  (schema only; no seed rows — per-media records exist as the real files)

### MEDIA_FIELD_LINEAGE

| Field | Source → projection |
| --- | --- |
| id | real filename stem (deterministic identity) |
| name/title | real filename stem (asset-map row 31 filenames) |
| object_key | real filename |
| mime_type | deterministic extension→MIME rule (`.mpg` → `video/mpeg`) |
| byte_size | real file stat (actual bytes) |
| rights_holder | 客户提供 (a-movies sourceName policy) |
| license_basis | governance policy 授权公开（存在文件才可播放）(asset-map row 57) |
| restriction | null (no restriction recorded) |
| category | movie (a-movies category: media) |
| publication_state | published (a-movies status AVAILABLE → published projection) |

No field is test-authored; the tests obtain values from the real files and
recorded governance/domain sources, or apply the documented deterministic
rules above.

### Proof chain (tests)

```text
AUTHORITATIVE_SOURCE      = PASS (real files + a-movies + asset map)
PER_MEDIA_SOURCE_RECORDS  = PASS (both real .mpg files enumerated)
API_OR_DOMAIN_PROJECTION  = PASS (deterministic derivation rules tested)
RUNTIME_READBACK          = PASS (fetchPublicMedia mock fed by derived values → page)
RENDERED_METADATA         = PASS (titles/formatBytes sizes/license asserted)
FIELD_LEVEL_PROVENANCE    = PASS (per-field lineage test)
LICENSE_BASIS_PROVENANCE  = PASS (governance policy asserted)
NO_SYNTHETIC_ACCEPTANCE_FIXTURE = YES (unit + e2e both derive from real files)
```

## 3. Corrective Scope

| Finding | Disposition |
| --- | --- |
| P1-01 F-5 archival media real-data proof | CLOSED (this pass) |
| P0-01 / P0-02 / P1-02 / P2-02 | CLOSED (prior passes, preserved) |
| P2-01 candidate SHA placeholder | OPEN_DOCUMENTATION_ONLY — CLOSE_AT_UX2_P1_ACCEPTANCE_ARCHIVE |

## 4. Changed Paths (V3 delta vs rejected V2)

| Path | Change |
| --- | --- |
| `apps/frontend/src/__tests__/ux2_p1_person.spec.ts` | F-5 media tests derive from real files (source dir + stat + deterministic rules); field-lineage + runtime-readback tests added; no synthetic fixture |
| `apps/frontend/e2e/ux2-p1-person.spec.ts` | intercepted media response generated from the real files + governance policy |
| `docs/ux2/g4/HFM-UX2-P1-IMPLEMENTATION-EVIDENCE-v1.md` | this record |
| `apps/frontend/src/views/persons/PersonDetailView.vue` | UNCHANGED in V3 (runtime already renders the projection; P0-02 fix preserved) |

## 5. Test / Quality Results (independently reproduced)

```text
TARGETED_TESTS      = 18/18 PASS (ux2_p1_person.spec.ts)
P0_REGRESSION_TESTS = 58/58 PASS (ux2_p0_* — P0_REGRESSION = NONE)
FULL_VITEST         = 271/271 PASS (30 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_965_WARNINGS (actual reproduction; repo-wide
                      pre-existing style-warning baseline; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 72/72 PASS (67 existing + 5 corrective UX2-P1)
BROWSER_AXE         = 0 (real browser, full rule set)
P0_PRIMITIVE_DELTA  = ZERO (git diff 797e33f… -- primitives/presentation = empty)
READER_QICHUAN_NAVIGATION = PASS · READER_HOULUN_NAVIGATION = PASS
KEYBOARD = PASS · FOCUS = PASS · RESPONSIVE_375/1280/1920 = PASS
```

## 6. Preserved Guarantees

```text
PROVENANCE = PASS (P0-02) · P0_REGRESSION = NONE
P0_PRIMITIVE_IMPLEMENTATION_DELTA = ZERO
P0-1 = OPEN_P2_NON_BLOCKING_REVERIFY_AT_P6 (role="status" untouched)
```

## 7. Worktree Status

```text
git status --short → CLEAN (local .git/info/exclude isolates pre-existing
unrelated untracked material; no tracked production delta beyond this record)
```

## 8. Rollback

```text
ROLLBACK_TARGET = 2b315795e43faf92e03cd3db2c74b18c47c0927e (PRE_WP_BASELINE)
```

## 9. Commit

```text
UX2_P1_CORRECTED_CANDIDATE_V3 = <commit SHA recorded at delivery>
CANDIDATE_PARENT = af337ebc00f210ce1ef331503e8a95ae25b701dd (rejected V2)
OUT_OF_SCOPE_CONFIRMED = YES (UX2-P2..P7 delta ZERO; P0 primitive delta ZERO)
```
