# HFM-UX2 Presentation Contract v1

Status: UX2-G1 NORMATIVE ARTIFACT · PRESENTATION_CONTRACT=FROZEN
Project: HFM Digital Humanities Experience 2.0
Frozen UI Baseline: `ae55abc606c419f27259fc80bb8bee258d595ce9`
UX2_G0: ACCEPTED · Current Gate: UX2-G1 · Implementation: NOT_AUTHORIZED · Code Change: PROHIBITED

This document is a **presentation contract only**. It defines normative behavior
for presentation primitives and shared scholarly presentation rules. It contains
no implementation code, introduces no domain entities, no backend fields, no APIs,
no databases, no clinical capabilities, and no inferred humanities relationships.

## 0. Contract Basis

Every requirement in this contract binds to the accepted frozen UI baseline and
its verified content invariants:

| Invariant | Value |
| --- | --- |
| Primary navigation | 5 links |
| Canonical person route | `/persons/person-huangfu-mi` |
| Audited papers / searchable | 515 / 5 |
| Jiayi edition records | 19 |
| Full-text reader documents | 2 (`后论` · `其传`) |
| Search index | 1 |
| Jiayi structured lineage | DATA-GAP |
| Heritage lineage structuring | PARTIAL |
| 刘君奇 generation | 第六代名医 |
| Rendering surfaces internal-path-free | confirmed |

Content states referenced below are the accepted `ContentStatus` vocabulary
(`AVAILABLE | METADATA_ONLY | DATA_GAP`) and the reader-specific
`ReadingAvailability` (`FULL_TEXT | EXCERPT | METADATA_ONLY`). No new state
vocabulary is created at the domain layer; presentation states in §7 are
presentation-derived only.

---

## 1. DHObjectLayout — Presentation Composition Primitive

### 1.1 Definition

`DHObjectLayout` is a presentation composition primitive. It exposes four
conceptual **regions**:

```text
Header
Context
Evidence
Relations
```

These regions are **presentation slots**, not domain entities. The primitive
carries four standing non-requirements:

```text
NO_NEW_DOMAIN_OBJECT       — the primitive adds no domain type.
NO_GRAPH_REQUIREMENT       — a graph engine is never required to render it.
NO_BACKEND_RESTRUCTURE     — it consumes existing projections only.
NO_RELATION_INFERENCE      — it never derives a relation that the data does not assert.
```

### 1.2 Slot Presence Contract

Each slot supports exactly one of three presence states:

```text
PRESENT
ABSENT_OPTIONAL
INCOMPLETE_WITH_EVIDENCE_STATE
```

**PRESENT** — render normally from authoritative data.

**ABSENT_OPTIONAL** — the slot collapses completely. Requirements:

- no empty container;
- no “暂无内容” card;
- no decorative placeholder;
- no reserved blank height;
- no disabled fake CTA.

**INCOMPLETE_WITH_EVIDENCE_STATE** — the slot MUST NOT silently disappear when
the incompleteness itself is meaningful. Triggering examples:

- only metadata exists (`METADATA_ONLY`);
- a source is explicitly recorded as lost;
- scholarly status is explicitly uncertain;
- the platform has incomplete structured data.

Render the corresponding verified presentation state (§7). This rule prevents
silent collapse from masking evidence conditions (NB-07, NB-08).

### 1.3 Header Slot Contract

`Header` renders only authoritative, verified display fields. Allowed content
classes:

```text
Object title / name
Object type
Verified identity
Verified dates
Verified period
Verified role
Presentation resource status
```

Prohibited behavior:

- invented subtitle;
- inferred historical role;
- visually completing missing metadata;
- promotional claims introduced only for composition balance.

### 1.4 Context Slot Contract

`Context` renders only explicit contextual facts already available from
authoritative HFM data. Eligible contexts:

```text
Person · Work · Edition · Publication · Historical event · Heritage project · Institution · Research activity
```

`Context` SHALL NOT manufacture relation semantics. Presenting two objects in
context is `ASSOCIATED_CONTEXT` or `CO_PRESENTED_ONLY` at most (§1.6), never an
implied `EXPLICIT_RELATION`.

### 1.5 Evidence Slot Contract

`Evidence` is not decoration. Every evidence item SHALL resolve to an
authoritative underlying evidence object or source reference. Eligible
presentation types:

```text
Source · Citation · Publication · Archive image · Media record · Holding/source institution · Document reference
```

Evidence affordances SHALL distinguish, where supported:

```text
resource available
metadata only
citation available
external source reference
```

The frozen baseline already renders these distinctions through `ContentStatus`
badges (`hfm-status`) and public source labels; the contract fixes that behavior
as normative for every `DHObjectLayout`.

### 1.6 Relations Slot Contract

Relations render only when the underlying relationship exists explicitly. Three
relation semantics are normative:

| Semantics | Meaning |
| --- | --- |
| `EXPLICIT_RELATION` | The underlying data explicitly asserts the relationship. |
| `ASSOCIATED_CONTEXT` | Objects share an approved contextual relationship but no stronger lineage or causal claim. |
| `CO_PRESENTED_ONLY` | Objects appear on the same thematic surface; no direct relation is implied. |

Visual rules SHALL prevent: lineage inference, causality inference, authorship
inference, transmission inference, edition-genealogy inference. Connecting
lines, arrows and genealogy trees require `EXPLICIT_RELATION` (NB-02, NB-03,
NB-04).

Baseline grounding: the heritage lineage surface renders only confirmed nodes
with a PARTIAL gap marker; the Jiayi edition surface keeps chronology
separate from lineage (DATA-GAP). Both behaviors are normative for UX2.

---

## 2. BibliographicRecord — Scholarly Record Primitive

### 2.1 Purpose

`BibliographicRecord` is the standard scholarly record primitive for eligible
objects: Works, Editions, Publications, Search results, Research results, Source
records.

### 2.2 Core Field Hierarchy

The minimum hierarchy uses only fields available in the frozen baseline. No
mandatory visual field may require unavailable backend data.

```text
Title
Responsible person/entity
Date or period
Edition/publication information
Resource/document type
Source/holding institution
Presentation state
Optional abstract/description
Optional citation locator
```

Field availability is classified per the API/Data non-expansion rule (§10):
absent fields degrade rather than being synthesized (NB-06).

### 2.3 Typography Behavior

Normative presentation principles:

```text
Hanging indent where appropriate
Low-decoration containers
Thin separators
Compact metadata
Readable scholarly rhythm
No marketing-card treatment
```

Exact CSS values are NOT part of this contract; they belong to G1-B.

---

## 3. Citation Contract

Citation is separated into two capabilities:

```text
CitationLocator
CitationExport
```

### 3.1 CitationLocator

MAY display precise existing citation data: work, edition, volume, chapter,
section, page, source reference. Only fields supported by authoritative data
may render. Missing locator fields SHALL NOT be synthesized.

Baseline grounding: the reader `CitationBlock` renders document-level and
citation-level locators only; it never invents 卷/页/版本号. Normative for UX2.

### 3.2 CitationExport

Potential formats MAY include: Plain citation, GB/T 7714, BibTeX. `CitationExport`
is capability-gated:

```text
IF all required source fields exist
AND transformation is deterministic
THEN export format MAY be enabled
ELSE export option SHALL NOT render
```

UX2-G1 does not require domain-model expansion to support citation export
(AC-04). Export output must never append promotional text.

---

## 4. Heritage Evidence-Context Separation

Heritage presentation defines two semantically distinct evidence contexts:

```text
HISTORICAL_TEXTUAL_CONTEXT
CONTEMPORARY_LIVING_ARCHIVE_CONTEXT
```

These are evidence-context categories, not necessarily permanent visual columns.

### 4.1 HISTORICAL_TEXTUAL_CONTEXT

Eligible verified evidence: classical texts, historical records, local
gazetteers, inscriptions, historical scholarship. Public presentation SHALL
clearly communicate the documentary/historical nature.

### 4.2 CONTEMPORARY_LIVING_ARCHIVE_CONTEXT

Eligible verified modern records: education/transmission activities, academic
meetings, research activity, studio/institution records, media reports, modern
documented events.

### 4.3 Separation Rule

The two contexts SHALL NOT be merged into a single uninterrupted transmission
timeline. Forbidden implied structure:

```text
ancient source → modern scholar → contemporary inheritor
```

unless every edge is independently and explicitly evidenced (NB-04).

Responsive layouts MAY represent the two contexts as two tracks, two sections,
two columns, sequential stacked regions, or tabbed contexts — provided semantic
separation remains intact (AC-05, AC-10).

Baseline grounding: the heritage surface renders the historical lineage
(皇甫谧 源头) and the contemporary archive (刘君奇·第六代名医, 师承, 工作室,
媒体报道) as distinct evidence contexts; the intermediate generations are a
PARTIAL gap, never drawn as an implied chain.

---

## 5. Presentation State Architecture

Three layers remain separate:

```text
SOURCE FACT
→ PRESENTATION STATE
→ PUBLIC LABEL
```

### 5.1 Required Presentation States

Candidate state vocabulary (presentation-only):

```text
RESOURCE_READY
METADATA_ONLY
SCHOLARLY_UNCERTAIN
HISTORICAL_ABSENCE
UNSTRUCTURED_OR_INCOMPLETE
```

These states are NOT introduced as new domain states. The accepted domain
`ContentStatus` and `ReadingAvailability` remain the underlying source-fact
layer.

### 5.2 Deterministic Mapping Requirement

The mapping function SHALL be:

```text
DETERMINISTIC
TOTAL_FOR_SUPPORTED_INPUTS
PRIORITY_DEFINED
FAIL_CLOSED
```

It is NOT described as injective: multiple legitimate source-fact combinations
may map to the same presentation state. The normative table is G1-C.

### 5.3 No Synthetic Fact Flags

The contract does NOT require invented fields such as `is_gap`, `is_uncertain`,
`is_complete`, `has_resource`. G1-C documents mappings using actual current
authoritative fields, or abstract evidence predicates explicitly marked
`DERIVED_PRESENTATION_ONLY` (AC-07).

### 5.4 Conflict Resolution

Where more than one presentation condition holds simultaneously, G1-C defines
precedence derived from semantic truthfulness, not visual desirability. The
following conflict classes are audited there (AC-06):

```text
resource available + scholarly uncertainty
resource unavailable + historical loss
metadata available + incomplete structuring
historical absence + platform incompleteness
```

No conflict may resolve ambiguously.

---

## 6. Public Label Contract

Public labels SHALL:

- communicate historical/data truth accurately;
- avoid engineering jargon;
- avoid implying certainty where none exists;
- avoid implying historical absence from simple data incompleteness.

Candidate labels (bound to explicit G1-C rules):

```text
数字资源可阅 · 全文已整理 · 存目 · 仅题录 · 待考 · 尚有争议 · 文献阙佚 · 原典未见 · 资料整理中 · 当前资料不完整
```

Every final label MUST be bound to an explicit G1-C mapping rule.

Baseline grounding: the frozen surface already distinguishes 已展示 / 元数据已录 /
整理中 via `hfm-status`; G1-C formalizes the full label set and precedence.

---

## 7. Responsive Contract

Every primitive SHALL define behavior across Desktop, Tablet, Mobile, and Large
exhibition display. Domain meaning SHALL NOT be encoded exclusively in:
horizontal position, column alignment, animation, hover, connector lines.
Mobile reflow MUST preserve meaning (AC-10, NB-10).

Baseline grounding: the frozen baseline is verified overflow-free at
375/768/1024/1440/1920 and at 200% zoom; mobile drawer/sidebar collapse keeps
semantic order. Normative for UX2.

---

## 8. Accessibility Contract

Minimum requirements:

```text
WCAG-oriented semantic structure
keyboard-operable interactions
visible focus
status text independent of color
no motion-dependent comprehension
appropriate heading hierarchy
accessible expandable citation content
```

The compliance target aligns with the project's already accepted accessibility
standard (axe-clean public and research surfaces on the frozen baseline, focus
ring, reduced-motion, 200% zoom verified). UX2-G1 invents no new project-wide
standard (AC-11, NB-11).

---

## 9. Homepage Contract Boundary

G1 MAY specify homepage composition grammar:

```text
Platform identity
Approved descriptor
Primary public entry
Secondary scholarly entry
Research workspace entry
Five-part exhibition narrative
```

G1 SHALL NOT author new historical/promotional content. Copy remains sourced
from approved HFM content (the frozen homepage narrative order is normative:
Hero → 皇甫谧 → 《针灸甲乙经》 → 文献与史料 → 非遗活态传承 → 研究能力).

---

## 10. API / Data Non-Expansion Rule

Every G1 component/API requirement classifies each required field as:

```text
EXISTING
DERIVED_PRESENTATION_ONLY
OPTIONAL
UNRESOLVED
```

No field may be labeled REQUIRED if fulfilling it would force unapproved
backend/schema expansion (AC-12). Items currently unconfirmable against the
frozen baseline are recorded in G1-C as `SOURCE_FIELD_UNRESOLVED` audit findings,
not implementation assumptions.

---

## 11. Acceptance Criteria

UX2-G1 passes only if all of the following hold (self-audit in §12):

```text
AC-01  DHObjectLayout has deterministic slot behavior.        (§1.2)
AC-02  BibliographicRecord has finite field + degradation rules. (§2)
AC-03  Citation locator and citation export are separated.    (§3)
AC-04  No citation format forces domain expansion.            (§3.2, §10)
AC-05  Historical and contemporary heritage contexts are semantically isolated. (§4)
AC-06  Presentation states are deterministic and conflict-resolved. (§5.2/5.4)
AC-07  No invented backend fact flags are required.           (§5.3)
AC-08  Token mappings preserve frozen visual identity.        (G1-B)
AC-09  Negative-boundary tests are executable as audit cases. (G1-D)
AC-10  Responsive behavior preserves semantics.               (§7)
AC-11  Accessibility behavior is contractually testable.      (§8)
AC-12  No domain model/API/database expansion is required.    (§10)
AC-13  No implementation code is changed.                     (baseline audit)
AC-14  Frozen baseline remains intact.                        (baseline audit)
```

---

## 12. Exit State

```text
UX2_G1 = ACCEPTED (subject to independent audit)
PRESENTATION_CONTRACT = FROZEN
IMPLEMENTATION = STILL_NOT_AUTHORIZED
NEXT_GATE = UX2-G2_PROTOTYPE
```

G2 shall build representative prototypes only against this accepted contract.
No general production implementation is authorized by G1 acceptance.
