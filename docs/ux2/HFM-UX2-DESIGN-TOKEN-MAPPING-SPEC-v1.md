# HFM-UX2 Design Token Mapping Spec v1

Status: UX2-G1 NORMATIVE ARTIFACT · Binds to frozen UI baseline `ae55abc…`
Scope: token deltas required by UX2 presentation primitives only.

## 0. Binding Rules

```text
NO_HARDCODED_HEX          — every visual value resolves to a semantic token.
NO_NEW_PALETTE            — no new color families; UX2 uses the frozen palette.
NO_ARBITRARY_ONE_OFF_TOKEN— a new token requires a cross-surface justification.
NO_LARGE_UI_LIBRARY       — no component/animation library dependency.
FROZEN_VISUAL_IDENTITY     — the frozen visual identity remains authoritative.
```

Dark/light behavior, contrast, border interaction and fallback are specified per
token below. Contrast targets follow the frozen AA record (text ≥ 4.5:1, large
text ≥ 3:1).

## 1. Semantic Surface Tokens

Candidate UX2 semantic roles and their mapping to EXISTING tokens.

### surface-paper

| Attribute | Value |
| --- | --- |
| Purpose | Primary reading/editorial surface (long-form, bibliography, quotations). |
| Allowed contexts | Reading pane, BibliographicRecord, Citation, quotation blocks. |
| Mapped existing token | `--hfm-color-surface` (light `#ffffff` / dark `#1e1a15`) |
| Dark/light | Automatic via semantic layer; no per-role override. |
| Contrast requirement | Text on surface ≥ 4.5:1 (`--hfm-color-text` on surface = 17.25 light). |
| Border interaction | `--hfm-color-border` / `--hfm-color-border-strong` hairlines only. |
| Fallback | `--hfm-color-surface` is the fallback for all surface-* roles. |

### surface-archive

| Attribute | Value |
| --- | --- |
| Purpose | Archive/facsimile framing (edition lineage image, document derivatives, status records). |
| Allowed contexts | Version-lineage figure frame, archive records, status-bearing records. |
| Mapped existing token | `--hfm-color-canvas` for ambient; records use `--hfm-color-surface`; frame border `--hfm-color-border`. |
| Dark/light | Automatic; facsimile images are NEVER inverted (kept in a surface frame). |
| Contrast requirement | Metadata on surface ≥ 4.5:1. |
| Border interaction | 1px border + restrained radius (`--hfm-radius-md`) on frames. |
| Fallback | `--hfm-color-canvas` → `--hfm-color-surface` fallback chain. |

### surface-evidence

| Attribute | Value |
| --- | --- |
| Purpose | Evidence/citation visual grounding (provenance, source, citation affordances). |
| Allowed contexts | EvidenceExplorer, CitationBlock, source/evidence badges. |
| Mapped existing token | `--hfm-color-evidence` (墨绿), `--hfm-color-citation` (靛青), `--hfm-color-success-surface`/`--hfm-color-azure` status surfaces. |
| Dark/light | Automatic; status surface tokens flip with `.dark`. |
| Contrast requirement | Status text ≥ 4.5:1 on its surface (verified AA record). |
| Border interaction | Left-rule/border accents only (`--hfm-radius-sm`); no floating cards. |
| Fallback | Evidence affordances degrade to plain text labels if a status token is unavailable. |

## 2. Typography Token Roles

Semantic roles, mapped to existing primitives. New tokens require
justification (§3).

| Role | Purpose | Mapped primitive |
| --- | --- | --- |
| type-object-title | DHObjectLayout header / object title | `--hfm-font-heading` (宋体系) · `--hfm-text-2xl/3xl`; hero overrides explicit per view |
| type-section-title | Page/section headings | `h2` default scale `--hfm-text-xl` |
| type-bibliographic-title | BibliographicRecord title line | `--hfm-font-heading` · `--hfm-text-lg` weight 600 |
| type-metadata | Compact metadata rows | `--hfm-font-sans` · `--hfm-text-sm/xs` · `--hfm-color-text-muted` |
| type-source | Source/来源 lines | `--hfm-font-sans` · `--hfm-text-xs/sm` · muted/secondary |
| type-footnote | Notes / provenance remarks | `--hfm-text-xs` · muted |
| type-status | Presentation-state labels | `--hfm-text-xs` · weight 600 · `.hfm-status[data-status]` token backgrounds |
| type-long-form | Reading text | `.hfm-reading` (`--hfm-font-ancient`, `--hfm-text-lg`, `--hfm-leading-reading`, `--hfm-reader-max`) |

Typography hierarchy is established by size/weight/letter-spacing, never by
heavy bolding alone (frozen guidance retained).

## 3. New-Token Justification Rule

A proposed token may be added only if it is:

1. cross-surface (used by ≥ 2 distinct surfaces), and
2. non-redundant (not expressible as an existing token composition).

As of this spec, every UX2 requirement maps to an existing token or utility
(`hfm-eyebrow`, `hfm-status`, `hfm-reading`, heading scale). No new token is
introduced; the list is closed unless G2 raises a justified delta, which would
require a G1 amendment.

## 4. Compliance Checks (bound to G1-D NB-09)

- Scan rule: rendered CSS/component files must not introduce hex not present in
  the frozen token set.
- Palette rule: no new color family tokens; heritage/cinnabar/azure/evidence/
  citation semantics unchanged.
- One-off rule: any `--hfm-*` addition triggers the justification rule §3.
