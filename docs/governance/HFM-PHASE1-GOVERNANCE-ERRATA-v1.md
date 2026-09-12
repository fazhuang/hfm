# HFM Phase 1 Governance Errata v1

Classification: `NON_SEMANTIC_ERRATA`  
Source candidate baseline: `acbaa6815df4261cee986894d4ba29c1d3845d90`  
NPG-11 finding: `P2 / NON-BLOCKING`

## Correction record

| Artifact | Old text | Corrected text |
| --- | --- | --- |
| `docs/governance/HFM-PHASE1-DEFINITION-OF-DONE-v1.md` DOD-02 | `26 edges` | `36 edges` |
| `docs/governance/HFM-PHASE1-DAG-v1.md` summary text | `The 26 edges above...` | `The 36 edges above...` |

The authoritative DAG edge table is unchanged: 14 nodes, 36 edges, 31 blocking edges, 5 non-blocking relation edges, cycles 0, unreachable nodes 0.

## Preserved semantics

- Scope semantics: unchanged (`IN = 14`, same dependency/deferred/rejected sets).
- Architecture semantics: unchanged.
- Acceptance and evidence semantics: unchanged.
- DoD semantics: unchanged; only the stale edge-count wording is corrected.
- No implementation, migration, schema, test, production import, ADR resolution, or CD-7 operation is introduced.
