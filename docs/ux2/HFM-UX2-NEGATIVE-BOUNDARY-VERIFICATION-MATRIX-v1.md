# HFM-UX2 Negative Boundary & Verification Matrix v1

Status: UX2-G1 NORMATIVE ARTIFACT · Executable audit cases · Binds to frozen
UI baseline `ae55abc…`. Each group defines a threat, the governing contract
rule, and an executable audit case. Existing frozen-baseline tests are cited
as executable evidence where they already cover the boundary.

## NB-01 Historical Fabrication

- Threat: UI copy fills missing historical facts.
- Rule: G1-A §1.3 Header prohibits invented subtitle/inferred role; G1-C labels
  never imply certainty where none exists.
- Audit case: scan all rendered presentation data (views/components minus
  comments) for fabricated fact patterns (e.g., invented birth/death years,
  invented honors, invented relationships); assert zero.
- Frozen baseline evidence: `ui12_correction` / `ui03_home` no-fabrication
  assertions; invariant `FAKE_METADATA_CREATED = NO`.

## NB-02 Relation Inference

- Threat: proximity, lines, arrows or chronology create unsupported
  relationships.
- Rule: G1-A §1.6 — connector lines/arrows/genealogy require `EXPLICIT_RELATION`;
  `CO_PRESENTED_ONLY` never implies relation.
- Audit case: assert that surfaces with multiple objects (Home features,
  Heritage sections, Jiayi related entries) contain no visual connector
  implying relation without an explicit edge; assert chronology timeline copy
  states `chronology ≠ lineage`.
- Frozen baseline evidence: ui08/jiayi “chronology ≠ lineage” assertion;
  ui09 lineage no-fabricated-edges tests.

## NB-03 Edition Genealogy

- Threat: edition lineage shown without explicit evidence.
- Rule: G1-A §1.6 + G1-C row 9 — `JIAYI_EDITION_RELATIONS = DATA-GAP`; the
  customer lineage PNG is a presentation asset, never a structured edge set.
- Audit case: assert the Jiayi surface renders no `继承自/源自/传自` edge
  claims; assert the DATA-GAP caption is present but not visually dominant.
- Frozen baseline evidence: ui08 “does not fabricate genealogical lineage
  edges” + “DATA-GAP” caption assertions.

## NB-04 Heritage Lineage

- Threat: uninterrupted ancient-to-modern inheritance chain implied.
- Rule: G1-A §4.3 — historical and contemporary contexts are semantically
  isolated; a single transmission timeline is forbidden unless every edge is
  evidenced.
- Audit case: assert the heritage surface renders 皇甫谧 (historical context)
  and 刘君奇 (contemporary archive) as distinct evidence contexts with an
  explicit PARTIAL gap marker; assert no first-to-fifth-generation names.
- Frozen baseline evidence: ui09 `UNVERIFIED_LINEAGE_NODES_CREATED = NO`,
  `LINEAGE_STRUCTURING: PARTIAL` tests.

## NB-05 Clinical Boundary

- Threat: treatment recommendation, acupoint recommendation, efficacy
  endorsement, prescription guidance, clinical decision support.
- Rule: frozen clinical boundary (non-clinical platform) retained.
- Audit case: scan all rendered presentation data for forbidden patterns
  (疗效显著/治疗推荐/适用于…疾病/预约/问诊/处方 guidance); assert zero.
- Frozen baseline evidence: ui03/ui06/ui07/ui08/ui09/ui11 clinical-boundary
  assertions; invariant `CLINICAL_MEDICAL_CONTENT = NO`.

## NB-06 Citation Fabrication

- Threat: missing page/volume/edition metadata synthesized.
- Rule: G1-A §3 — CitationLocator renders only existing fields; CitationExport
  is capability-gated.
- Audit case: assert reader data contains no invented 卷/页/版本号; assert
  export options render only when all required fields exist.
- Frozen baseline evidence: ui07 “citation never invents volume/page/edition” +
  CitationBlock determinism tests.

## NB-07 State Misrepresentation

- Threat: missing platform data ≠ historical absence; missing full text ≠
  document lost; uncertainty ≠ incompleteness.
- Rule: G1-C §3 precedence + §2 rows 4/6/7 — loss is never inferred from data
  absence; controversy is never downgraded to incompleteness.
- Audit case: for each state row, assert the rendered label matches the
  governing input condition (e.g., 四论 → 仅题录（原典全文未收录）, never
  文献阙佚 unless loss asserted).
- Frozen baseline evidence: ui07 METADATA_ONLY reader states; yan collection
  supplement (逸士传 辑佚 → 文献阙佚 predicate only where text asserts 散佚).

## NB-08 Empty Slot Behavior

- Threat: optional absent slots collapse without empty UI shells; evidence-
  bearing incompleteness becomes invisible.
- Rule: G1-A §1.2 — ABSENT_OPTIONAL collapses fully; INCOMPLETE_WITH_EVIDENCE_STATE
  renders the verified state.
- Audit case: assert no “暂无内容” placeholder cards render for optional
  absent slots; assert METADATA_ONLY/DATA_GAP surfaces render status text, not
  blank bodies.
- Frozen baseline evidence: ui06 archive status rendering; ui07 reader
  METADATA_ONLY status page; ui08 empty-state handling.

## NB-09 Token Compliance

- Threat: hard-coded palette drift.
- Rule: G1-B §4 — no hex outside the frozen token set; no new palette.
- Audit case: scan all rendered CSS/Vue presentation for hex not in the frozen
  token set; assert zero additions.
- Frozen baseline evidence: `HARD_CODED_COLOR_DRIFT = NO` scans from UI-13.

## NB-10 Responsive Semantics

- Threat: mobile layout loses relation/evidence semantics when spatial layout
  changes.
- Rule: G1-A §7 — domain meaning never encoded exclusively in horizontal
  position/columns/hover/connectors; reflow preserves meaning.
- Audit case: assert 375px overflow-free on all major surfaces and that
  lineage/evidence/status elements remain present (possibly stacked) at mobile.
- Frozen baseline evidence: 375/768/1024/1440/1920 + 200% zoom e2e matrix;
  mobile drawer/sidebar semantic-order tests.

## NB-11 Accessibility

- Threat: status color-only, keyboard unreachable, heading/focus/motion issues.
- Rule: G1-A §8 — status text independent of color, keyboard operable, visible
  focus, reduced-motion compatible, heading hierarchy.
- Audit case: axe = 0 violations on major surfaces; assert status labels carry
  text not color alone; assert focus ring present; assert reduced-motion.
- Frozen baseline evidence: axe assertions across ui04/06/07/08/09/10/11;
  focus-ring e2e; reduced-motion global rule.

## NB-12 Frozen Baseline Integrity

- Threat: G1 introduces implementation code changes or mutates the frozen
  baseline.
- Rule: G1 scope = documentation/contracts only.
- Audit case: `git rev-parse HEAD` must remain `ae55abc…`; `git status --short`
  tracked delta must be zero; no `apps/**` change attributable to UX2-G1.
- Frozen baseline evidence: baseline SHA audit performed at G1 delivery.

## Verdict Binding

Each audit case is executable against the frozen baseline or a G2 prototype
built from this contract. A case is PASS only when the assertion holds on the
accepted implementation; failures block UX2-G1 acceptance per AC-09.
