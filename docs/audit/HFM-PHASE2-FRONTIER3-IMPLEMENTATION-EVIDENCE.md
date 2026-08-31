# HFM Phase 2 — Frontier-3 Implementation Evidence

Status: FORMAL TRACKED EVIDENCE · Frontier-3 (P2-03, P2-04, P2-06, P2-08, P2-09) · machine-executed
Governance Baseline: `7fa7c4f60244daa6999e377d08502bde522c56b2`
Frontier-2 Acceptance Baseline: `e2d9440f4e4d34e5a0a599d3191bfbb27fd9333e`
Rejected Frontier-3 Candidate: `b0979e2258b3ec2d58d9d67a149965f11b37b213`
Corrected Frontier-3 Candidate: this commit（自引用；实际 SHA 于提交后记录）
Execution timestamp: 2026-08-31T05:31:54Z / 2026-08-31T05:32:15Z

## Evidence matrix (15 mandatory Evidence IDs)

| Evidence ID | WP | AC | Implementation artifact | Authoritative test command | Test count | Result |
| --- | --- | --- | --- | --- | --- | --- |
| E2-08 | P2-03 | P2-03-AC-01 | services/reader.ts (resolveLocator, locatorKey) | `pnpm exec vitest run src/__tests__/p2_03_reader_search.spec.ts` | 10 | PASS |
| E2-09 | P2-03 | P2-03-AC-02 | views/reader/ReaderView.vue (published-only rendering) | same suite (draft/withdrawn hidden tests) | 10 | PASS |
| E2-10 | P2-03 | P2-03-AC-03/04 | services/reader.ts (searchPublished), views/search | same suite (role scoping + forbidden-term tests) | 10 | PASS |
| E2-11 | P2-04 | P2-04-AC-01 | services/heritage.ts (visibleNodes/Relations), LineageTree.vue | `pnpm exec vitest run src/__tests__/p2_04_heritage.spec.ts` | 8 | PASS |
| E2-12 | P2-04 | P2-04-AC-02 | services/heritage.ts (unverified/private filter) | same suite (negative node tests) | 8 | PASS |
| E2-13 | P2-04 | P2-04-AC-03 | views/heritage/HeritageView.vue (EmptyState) | same suite (empty-genealogy tests) | 8 | PASS |
| E2-17 | P2-06 | P2-06-AC-01 | phase2/export/service.py (DISCLAIMER retention) | `python -m pytest tests/test_phase2_export.py -q` (backend) + `pnpm exec vitest run src/__tests__/p2_06_export.spec.ts` (frontend) | 4 + 7 | PASS |
| E2-18 | P2-06 | P2-06-AC-02 | phase2/export/service.py (withdrawn/draft blocked) | same backend suite (ExportError tests) | 4 | PASS |
| E2-19 | P2-06 | P2-06-AC-03 | phase2/export/service.py (deterministic output) | same suites (determinism tests) | 4 + 7 | PASS |
| E2-23 | P2-08 | P2-08-AC-01 | core/logging_probes.py (health/ready) | `python -m pytest tests/test_phase2_observability.py -q` + `infra/scripts/health-check.sh` | 5 + 1 | PASS |
| E2-24 | P2-08 | P2-08-AC-02 | infra/scripts/release-gate.sh + verify-governance-precheck.sh | `infra/scripts/release-gate.sh` (GOVERNANCE_PRECHECK=PASS; RELEASE_GATE=PASS) | 1 | PASS |
| E2-25 | P2-08 | P2-08-AC-03 | core/logging_request_log.py (structured request log) | same observability suite (structured log tests) | 5 | PASS |
| E2-26 | P2-09 | P2-09-AC-01 | services/audit.ts, views/admin/AuditLogView.vue (role-gated) | `pnpm exec vitest run src/__tests__/p2_09_audit_view.spec.ts` | 7 | PASS |
| E2-27 | P2-09 | P2-09-AC-02 | services/audit.ts (GET-only, no mutation) | same suite (read-only tests) | 7 | PASS |
| E2-28 | P2-09 | P2-09-AC-03 | views/admin/AuditLogView.vue (reconciliation PASS/FAIL) | same suite (state display tests) | 7 | PASS |

All commands were re-executed this round; every result recorded above is the actual
machine output (exit 0, 0 failed). No result is carried over from prior Pi output.

## Browser E2E (P1-02)

- Command: `pnpm e2e` (Playwright test)
- Working directory: `/Users/likeming/Sites/hfm/apps/frontend`
- Browser/project: Playwright chromium headless-shell (configured in playwright.config.ts)
- Web-server command: `pnpm dev --port 5199 --strictPort` (webServer with reuseExistingServer)
- Port: 5199
- Tests: 10 | Passed: 10 | Failed: 0 | Exit: 0
- Coverage: P2-01-AC-01 anonymous portal traversal; AC-02 published projection
  (draft/withdrawn hidden); AC-03 anonymous research/admin redirect; viewport matrix
  (sm/md/lg) layout, overflow, navigation
- Timestamp: 2026-08-31T05:31:54Z

## Release-gate governance fail-closed (P0-01)

- `infra/scripts/verify-governance-precheck.sh` runs the canonical supersession
  verifier (requires exit 0 and `SUPERSESSION_REGISTER=PASS`), extracts the formally
  superseded Class H test scopes from the register, validates every governed
  deselection node (coverage + disjoint from ACTIVE replacements), and FAILS CLOSED
  on any governance failure.
- Adversarial suite `infra/scripts/test-release-gate-precheck.sh`: A verifier fails,
  B verifier unavailable, G/H verifier non-PASS signal, C malformed register,
  D assertion no longer superseded, I mapping missing, E unauthorized deselection,
  J injected deselection, F active-replacement deselection — all FAIL closed;
  valid state PASS. `RELEASE_GATE_PRECHECK_ADVERSARIAL=PASS`.
- Release gate run: `GOVERNANCE_PRECHECK=PASS` then `RELEASE_GATE=PASS`.

## Candidate binding

Evidence is bound to the Corrected Frontier-3 Candidate (this commit; SHA recorded
post-commit), which descends from the rejected candidate `b0979e2…` and the accepted
Frontier-2 Acceptance Baseline `e2d9440…` under Governance Baseline `7fa7c4f…`.
