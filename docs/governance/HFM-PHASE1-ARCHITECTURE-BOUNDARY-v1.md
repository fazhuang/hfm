# HFM Phase 1 Architecture Boundary v1

Status: NPG-7 GOVERNANCE OUTPUT · BOUNDARIES FROZEN AS REQUIREMENTS  
Branch: `governance/next-phase-authorization`  
Parent baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`  
Authority: NPG-6 scope verdicts are fixed inputs. This document does not authorize implementation.

## 1. Architecture principle

**Architecture Greenfield + Capability Brownfield**:

- HFM owns the canonical domain, provenance semantics, publication state, and authorization boundaries.
- Existing HFM canonical models are the foundation; they do not imply that product surfaces already exist.
- HFB may provide patterns or migration inputs only through explicit adapters, mappings, validation, and contracts.
- HFM must have no permanent HFB runtime dependency.
- Public and research experiences may share governed core services, but are separate experiences and authorization surfaces.
- Platform capability, content population, and public publication are separate acceptance dimensions.

## 2. Required boundary decisions

| ID | Boundary | Classification | Frozen boundary rule |
| --- | --- | --- | --- |
| AB-01 | HFM canonical domain ownership | REQUIRED_BOUNDARY | Entity, Work/Edition/Version/Passage, Evidence, Assertion, Citation, Event and relations remain HFM-owned canonical truth. |
| AB-02 | Public Portal vs Research Experience | REQUIRED_BOUNDARY | Public browsing/search/reader expose approved published content only; research workflows require authentication and policy. |
| AB-03 | Shared Content Core | REQUIRED_BOUNDARY | One governed content identity/lineage model may serve both experiences; no independent duplicate truth stores. |
| AB-04 | Shared Evidence/Citation/SourceRef semantics | REQUIRED_BOUNDARY | Both experiences use the HFM SourceRef→Evidence→Citation semantics; display detail varies by authorization. |
| AB-05 | Knowledge relations A/B/C/D | REQUIRED_BOUNDARY | Cross-domain links are explicit, evidence/version/publication-aware relations; each domain has ownership, not a duplicate graph truth. |
| AB-06 | Content Admission | REQUIRED_BOUNDARY | Source/artifact admission requires identity, provenance, rights state, validation, and fail-closed rejection before use. |
| AB-07 | Publication/withdrawal | REQUIRED_BOUNDARY | Publication is a reviewed projection/state separate from research data; withdrawal and rollback are observable and enforceable. |
| AB-08 | RBAC | REQUIRED_BOUNDARY | Identity, roles, tenant/institution policy, and separation of duties protect research and management operations; deny by default. |
| AB-09 | Reader | REQUIRED_BOUNDARY | Reader addresses a specific version/passage/source locator and preserves quotation and evidence context; it is not a generic document viewer. |
| AB-10 | Search | REQUIRED_BOUNDARY | Search applies publication and authorization filters and preserves source/version context; public and research result policies differ. |
| AB-11 | Version/provenance/audit | REQUIRED_BOUNDARY | Version lineage, source hashes, editorial/publication state, and action history remain traceable and immutable where required. |
| AB-12 | HFB adapter/migration | REQUIRED_BOUNDARY | HFB data/code crosses only through a versioned mapping contract, validation, reconciliation, and explicit disposition. |
| AB-13 | No HFB runtime dependency | FORBIDDEN_COUPLING | HFM runtime, deployment, availability, and authorization must not require HFB services, database, routes, or credentials. |
| AB-14 | No clinical decision-support semantics | FORBIDDEN_COUPLING | C supports historical textual retrieval only; no diagnosis, treatment, prescription, ranking, efficacy, or automatic 主穴/配穴 recommendation. |
| AB-15 | Production content import vs deployment | REQUIRED_BOUNDARY | Platform deployment and content import are separate gates; dry-run or adapter validation is not production import. |
| AB-16 | Deferred modules | FORBIDDEN_COUPLING | Display, HFB UI reuse, AI, 3D, VR, XR, and virtual training may not add dependencies to the Phase 1 core. |

## 3. Canonical content layers and invariants

The architecture must represent, without choosing a database product:

`Source → Artifact → Version → Provenance → Evidence → Citation → Entity/Relation → Publication State`

Required invariants:

1. Every admitted artifact has an owner/source identity, content hash where applicable, provenance status, rights status, and validation result.
2. A Version belongs to an explicit Work/Edition lineage; a Passage locator is version-specific and reproducible.
3. Evidence is anchored to a SourceRef or valid passage locator; Citation targets an accepted assertion and retains version context.
4. Entity and cross-domain Relation records identify their evidence, version, editorial status, and publication state.
5. Unknown rights or failed provenance never become public content.
6. Research-only records cannot be returned by public endpoints or public search indexes.
7. Publication withdrawal removes or suppresses the public projection without deleting research evidence or falsifying history.
8. Content batches can be retried/reconciled without changing canonical identity or silently overwriting reviewed records.

## 4. Domain boundaries

| Domain | Ownership | Cross-domain rule |
| --- | --- | --- |
| A 人物体系 | Person, biography/event assertions and identity records | Links to B/C/D only through explicit, evidenced relations and publication state. |
| B 文献/思想体系 | Work, Edition, Version, Chapter, Passage and interpretive assertions | Interpretations remain distinguishable from source evidence and inherit version/rights constraints. |
| C 《针灸甲乙经》 | Versioned textual knowledge and historical relations among 病证、章节、穴位、经络、刺灸法 | Retrieval may show historical relationships and citations; it cannot expose clinical advice semantics. |
| D 非遗传承体系 | Heritage project, inheritor, lineage/event assertions and official-name evidence | Formal project identity, personal permissions, and public status are independently evidenced. |

No domain may maintain an independent competing truth store for shared persons, works, versions, sources, or evidence.

## 5. Public/research separation

### Public Experience

Public browsing, public search, and public reading consume an approved publication projection only. They must not expose research notes, unapproved evidence, internal source files, private personal data, or draft states.

### Research Experience

Authenticated researchers use richer source/evidence access, research projects, notes, and non-public materials according to RBAC and institutional policy. Research state is not public content merely because it is searchable internally.

Shared services are allowed only when authorization, projection, logging, and response filtering remain explicit. Shared ambiguous routes or an assumption that the Research Backend is the Public Portal are forbidden.

## 6. HFB dependency boundary

The HFB Evidence/SourceRef/Citation item is `DEPENDENCY_ONLY` under NPG-6. Any later migration must bind:

- exact HFB source snapshot and artifact manifest;
- a versioned mapping into HFM canonical targets;
- validation of locator, provenance, rights, hashes, and identity collisions;
- reconciliation report with accepted/rejected/quarantined rows;
- fail-closed behavior for unmapped, unsupported, unauthorized, or medically unsafe records;
- retry/idempotency and rollback evidence;
- zero HFB runtime, database, route, credential, or availability dependency after migration.

HFB Library/Reader/Workspace/RBAC/UI assets remain candidate adaptations, not architectural commitments.

## 7. Technology neutrality

Neo4j, Elasticsearch, MinIO/OSS, WebSocket, and any specific database, search, object-storage, or transport product are ADR candidates only. This boundary document freezes contracts and separation properties, not products.
