# HFM Phase 2 DAG v1

Status: GOVERNANCE CANDIDATE · ACYCLIC CONTRACT (design) · READY FOR INDEPENDENT AUDIT
Nodes: 11 · Edges: 12 · Blocking: 10 · Non-blocking: 2 · Cycles: 0 · Unreachable: 0

## Nodes

`P2-00, P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10`

## Edges

| FROM | TO | Dependency reason | Blocking | Required evidence |
| --- | --- | --- | --- | --- |
| P2-00 | P2-01 | Governance contract precedes public frontend foundation | YES | governance trace |
| P2-00 | P2-02 | Governance contract precedes research/admin foundation | YES | governance trace |
| P2-00 | P2-05 | Media ADR + governance precede media lifecycle | YES | ADR-P2-01 decision |
| P2-00 | P2-07 | Deployment ADR + governance precede deployment foundation | YES | ADR-P2-02 decision |
| P2-00 | P2-10 | Reuse adjudication is governance work | YES | adjudication register |
| P2-01 | P2-03 | Public foundation precedes reader/search surfaces | YES | frontend foundation build |
| P2-01 | P2-04 | Public foundation precedes heritage visualization | YES | frontend foundation build |
| P2-02 | P2-06 | Research/admin foundation precedes export/print | YES | research foundation build |
| P2-02 | P2-09 | Research/admin foundation precedes admin audit view | YES | research foundation build |
| P2-07 | P2-08 | Deployment foundation precedes observability/release gates | YES | deployment foundation build |
| P2-03 | P2-04 | Reader/search drill-down integrates visualization (relation edge) | NO | integration trace |
| P2-05 | P2-01 | Media-bearing public display consumes media API when present (relation edge; portal is not blocked by media lifecycle) | NO | media display fixture |

## Dependency principles (design audit)

- Frontend foundation precedes all portal/research/reader/search surfaces (P2-01, P2-02 → P2-03, P2-04, P2-06, P2-09).
- Media ADR (ADR-P2-01) gates media lifecycle; media lifecycle feeds media-bearing public display non-blockingly (portal acceptance never waits on media content).
- Deployment ADR (ADR-P2-02) gates deployment foundation; observability/release gates build on deployment foundation.
- HFB reuse adjudication gates any future PORT/ADAPT work; Phase-2 IN scope contains no PORT/ADAPT work package, so the gating edge is satisfied vacuously and documented.
- No edge is derived from numbering; every edge is derived from the dependency principles in the Work Package Contract.
- P2-C1/C2/C3/C4 are not blocked by full customer content population; fixture-based acceptance is the default policy.

## Topology

- ROOTS: `[P2-00]`
- LEAVES: `[P2-04, P2-05, P2-06, P2-08, P2-09, P2-10]`
- CYCLE_COUNT: 0 (DFS-verified over the full edge set)
- UNREACHABLE_COUNT: 0 (single root; reachability over blocking graph and full DAG)
