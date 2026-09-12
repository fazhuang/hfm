# HFM UI Freeze Candidate

Status: `FREEZE_CANDIDATE_READY`
Candidate HEAD: `094713bd06c56ef67499724925cb8a2219e1b4c8`
Audit evidence: `docs/design/HFM-UI-FINAL-ACCEPTANCE-EVIDENCE.md`

## Included scope

UI-01 Design Foundations; UI-02 Global Shell / Navigation; UI-03 Homepage;
UI-04 Huangfu Mi Profile; UI-06 Literature / Yan / Works / Archive; UI-07
Reader; UI-08 Jiayi Jing; UI-09 Heritage; UI-10 Search / Bibliography; UI-11
Research Workbench; UI-12 Cross-Surface Audit; UI-13 Visual Polish.

UI-05 Timeline is an absorbed dependency component. AI, RAG, 3D/WebGL, VR/XR,
annotation backend, notebook, collaboration, full-text migration, first-to-
fifth-generation heritage reconstruction, structured Jiayi lineage inference,
the four missing ancient full texts, and complete 515-paper structuring remain
excluded/deferred.

## Freeze gates

- P0 = 0; P1 = 0.
- 20 registered leaf routes covered; five-item primary navigation passes.
- 515 audited papers / 5 searchable paper records; one search index.
- 19 edition records; two full-text reader documents.
- Jiayi lineage `DATA-GAP`; heritage lineage `PARTIAL`; 刘君奇 `第六代名医`.
- Privacy, copyright, clinical boundary, HFB zero-coupling, RBAC, and Phase-2
  regression checks pass.
- Light/dark, responsive, keyboard/focus, axe, and 200% zoom checks pass.
- `195/195` Vitest, `67/67` Playwright, typecheck, lint, format, build, and
  `git diff --check` pass.
- Governance and formal Phase-2 baselines are untouched.
- Customer source assets `hfmzl/` and `zzcl/` are unchanged by the audit.

## Worktree and observations

The candidate is not committed as a UI implementation candidate in this audit:
the worktree retains the existing uncommitted UI changes and customer/design
material. Known non-blocking observations are historical lint warnings, jsdom
Canvas tooling warnings, and the lens-guard session note. No new dependencies,
governance changes, or customer-source writes were introduced.

This is a freeze-candidate document only. It is not an Acceptance Archive, a
formal UI baseline, a commit, a tag, or a declaration that the repository is
archived/frozen.

## Verdict

`UI_14_FREEZE_CANDIDATE_READY`
