# HFM-UX2 G3 Design Acceptance Package v1

Status: UX2-G3 NORMATIVE ARTIFACT · Package-ready for independent audit
Frozen UI Baseline: `ae55abc606c419f27259fc80bb8bee258d595ce9`
Binding inputs:

- G1 contracts (ACCEPTED): `docs/ux2/HFM-UX2-PRESENTATION-CONTRACT-v1.md` ·
  `HFM-UX2-DESIGN-TOKEN-MAPPING-SPEC-v1.md` · `HFM-UX2-PRESENTATION-STATE-MATRIX-v1.md` ·
  `HFM-UX2-NEGATIVE-BOUNDARY-VERIFICATION-MATRIX-v1.md`
- G2 evidence (ACCEPTED): `docs/ux2/g2/HFM-UX2-G2-PROTOTYPE-PLAN-v1.md` ·
  `HFM-UX2-G2-PROTOTYPE-DATA-BINDING-v1.md` · `HFM-UX2-G2-PROTOTYPE-ACCEPTANCE-MATRIX-v1.md` ·
  `HFM-UX2-G2-PROTOTYPE-AUDIT-REPORT-v1.md` · `HFM-UX2-G2-CORRECTIVE-PASS-v1.md`
- Independent acceptance: `UX2_G2_ACCEPTED`

G3 mandate: accept or reject the design system as the basis for a future G4
Implementation Authorization deliberation. G3 does NOT redesign, extend, or
re-explore. The design language below is FROZEN as of this package.

## 0. Governance Binding

```text
UX2-G0 = ACCEPTED
UX2-G1 = ACCEPTED
UX2-G2 = ACCEPTED
CURRENT_GATE = UX2-G3
UX2-G4 = NOT_AUTHORIZED
PRODUCTION_IMPLEMENTATION = LOCKED
```

G3 is not production implementation. G3 changes governance documentation only.

## 1. Frozen Design Language

```text
Digital Humanities Knowledge Interface

Object
  → Context
  → Evidence
  → Relations
```

The knowledge interface presents a scholarly object, then grounds it in its
verified context, its evidence, and its explicitly asserted relations — never
in an implied narrative chain. This progression is the single organizing
syntax of the UX2 design language (G1-A §1 DHObjectLayout).

Frozen semantic properties:

```text
EVIDENCE_FIRST        — every claim surface renders its source/status.
OBJECT_CENTERED       — pages present objects, not marketing.
RESTRAINT             — low-decoration, editorial, scholarly rhythm.
TRUTHFUL_INCOMPLETENESS — unresolved data degrades visibly, never silently.
```

## 2. Interface Grammars (four)

Frozen from G1 + proven in G2. These are the four interface grammars of the
UX2 design system:

| # | Grammar | Canonical object | G2 proof |
| --- | --- | --- | --- |
| 1 | Person / Historical Archive | 皇甫谧 (P-G2-01) | `p01-person.html` — DHObjectLayout header/context/evidence/relations; optional slots collapse; scholarly-uncertain & metadata-only incomplete states |
| 2 | Classical Text / Bibliographic Resource | 《针灸甲乙经》 (P-G2-02) | `p02-jiayi.html` — work → 19 edition BibliographicRecords (存目) → FULL_TEXT 2 → edition-relations DATA-GAP |
| 3 | Living Heritage Archive | 皇甫谧针灸非遗 (P-G2-03) | `p03-heritage.html` — HISTORICAL_TEXTUAL_CONTEXT vs CONTEMPORARY_LIVING_ARCHIVE_CONTEXT separation; PARTIAL lineage gap; recognition as secondary metadata (8/8, no honor wall) |
| 4 | Scholarly Discovery | 研究检索 (P-G2-04) | `p04-discovery.html` — facets from search-index type counts (515 audited / 5 searchable); BibliographicRecord results; CitationLocator at document level (page-level collapsed, U-04) |

A fifth composition context, Homepage Exhibition Narrative (P-G2-05), applies
the same grammar to platform orientation and is frozen as part of the system.

## 3. Core Primitives (two)

Both primitives are ACCEPTED design primitives, proven reusable across surfaces
in G2 (index.html + five surfaces). Their contracts are frozen in G1-A; G2
demonstrated the slot/kind matrix.

### 3.1 DHObjectLayout

```text
Regions:        Header · Context · Evidence · Relations
Slot presence:  PRESENT | ABSENT_OPTIONAL | INCOMPLETE_WITH_EVIDENCE_STATE
Relations:      EXPLICIT_RELATION | ASSOCIATED_CONTEXT | CO_PRESENTED_ONLY
Object title:   presentation-level heading, adapts to document outline
                (G2 F-1 mechanism: titleTag contract; see N-F-1 register)
```

G2-proven behaviors: optional slots collapse with no empty shell; evidence-
bearing incompleteness renders its verified state (`role=status`); object
title level fits the hosting surface's heading hierarchy.

### 3.2 BibliographicRecord

```text
Kinds proven:   classical work · edition · paper · search result · source reference
Field hierarchy: Title → responsible entity → date/period → edition/publication →
                type → source → presentation state → optional abstract/locator
Degradation:    absent fields degrade; never synthesized (NB-06)
```

## 4. Representative Surfaces (five)

Frozen surface set with G2 acceptance evidence:

| Surface | Path | G2 result |
| --- | --- | --- |
| P1 Person Archive | `p01-person.html` | PASS — object-first person archive; incomplete states rendered; heading hierarchy corrected (F-1) |
| P2 Jiayi Work / Edition | `p02-jiayi.html` | PASS — 19 editions as 存目; 2 FULL_TEXT; DATA-GAP; no genealogy inferred |
| P3 Heritage Living Archive | `p03-heritage.html` | PASS — two semantic contexts; PARTIAL gap; recognition 8/8 secondary metadata (F-4) |
| P4 Scholarly Discovery | `p04-discovery.html` | PASS — facets = search-index type counts (F-3 clarified); 515/5; document-level CitationLocator |
| P5 Homepage Exhibition Narrative | `p05-home.html` | PASS — approved copy; five-part narrative in frozen order; weak research entry |

Plus the primitive hub (`index.html`) proving both primitives across slot
states and record kinds. All six surfaces: axe 0 violations, 0 horizontal
scroll at 375/1920, PT-NB-01…12 PASS (re-verified in the corrective pass).

## 5. Design Decisions Accepted (no redesign)

The following are accepted design decisions of the frozen system; G4
implementation shall follow them, not revisit them:

```text
OBJECT-FIRST COMPOSITION        — DHObjectLayout regions order is normative.
EVIDENCE AFFORDANCES            — source/citation affordances always shown.
STATE VOCABULARY                — 5 presentation states with G1-C precedence.
PUBLIC LABEL SET                — 数字资源可阅/全文已整理/存目/仅题录/待考/尚有争议/
                                  文献阙佚/原典未见/资料整理中/当前资料不完整.
HERITAGE TWO-CONTEXT SEPARATION — historical vs contemporary never merged into
                                  one transmission timeline.
RELATION SEMANTICS BOUNDED      — 3 normative semantics; no lineage/causality
                                  inference from proximity.
CLINICAL ZERO-TOLERANCE         — no treatment/acupoint/efficacy content.
HOME NARRATIVE ORDER            — Hero → 皇甫谧 → 《针灸甲乙经》 → 文献与史料 →
                                  非遗活态传承 → 研究能力 (frozen order).
NO HONOR WALL                   — recognition is secondary metadata.
```

## 6. Visual Identity

The design language's visual identity is frozen to the accepted token system:
frozen palette projected value-identically (35/35, `NEW_PALETTE=ZERO`,
`TOKEN_DRIFT=ZERO`), semantic token roles per G1-B, editorial scholarly
composition, no SaaS-dashboard / government-portal / marketing-landing /
news-aggregation / museum-gimmick / AI-product visual language.

## 7. Decision

```text
DESIGN SYSTEM VERDICT = ACCEPT
```

The G1 contract and G2 prototype evidence together establish a coherent,
bounded, evidence-first design system. G3 accepts the design language as the
basis for a future G4 Implementation Authorization deliberation. No redesign
is proposed or authorized by this acceptance.

## 8. Exit State

```text
UX2_G3 = PACKAGE_READY / PENDING_INDEPENDENT_AUDIT
UX2_G4 = NOT_AUTHORIZED
PRODUCTION_IMPLEMENTATION = LOCKED
```

Companion G3 artifacts: `HFM-UX2-G3-IMPLEMENTATION-SCOPE-MATRIX-v1.md` ·
`HFM-UX2-G3-RISK-AND-DEFERRED-ITEMS-v1.md` ·
`HFM-UX2-G3-AUTHORIZATION-READINESS-REPORT-v1.md`.
