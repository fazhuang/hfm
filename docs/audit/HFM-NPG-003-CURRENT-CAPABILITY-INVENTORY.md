# HFM NPG-3 — Current HFM Capability Inventory

Date: 2026-08-29
Audited Git object: `0167b1702dac13993a5206f63752eafcc8e5387e`
Rule: repository facts only; plans and HFB capabilities are not counted as HFM capabilities.

## 1. Status semantics

- **IMPLEMENTED** — executable code/schema exists at the baseline.
- **PARTIAL** — a real subset exists, but not the named end-user capability end to end.
- **STUB** — executable placeholder/scaffold.
- **DOCUMENT_ONLY** — described but not implemented.
- **ABSENT** — no implementation found at the baseline.

## 2. Capability matrix

| CAP-ID | Capability | Repository Location | Status | Test Evidence | Dependency | Architecture Coupling | Production Readiness | Current Consumer | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAP-001 | Backend application | `apps/backend/src/hfm/main.py`, `core/`, `middleware/`, `db/` | PARTIAL | Fresh baseline pytest/ruff/mypy PASS | FastAPI, SQLAlchemy, Alembic, asyncpg | Medium: PG-oriented domain foundation | FOUNDATION_ONLY | Health/system probes; tests | Entrypoint explicitly says skeleton; no business router mounted |
| CAP-002 | Frontend application | `apps/frontend/src/App.vue`, `router/index.ts`, `views/HomeView.vue` | STUB | Fresh lint/typecheck/Vitest/build PASS; 24 tests | Vue 3, Router, Pinia, Vite | Low | NOT_READY | Skeleton home page | One `/` route; marker “Repository Skeleton Ready” |
| CAP-003 | Canonical domain | `models/{entity,person,institution,work,edition,version,chapter,passage,source,source_ref,evidence,assertion,citation,event,event_relation}.py` | IMPLEMENTED | Model, invariant, repository and DB-probe tests | SQLAlchemy | High: frozen HFM canonical model | FOUNDATION_ONLY | Repositories/tests | Data model exists; not exposed as product APIs |
| CAP-004 | Database schema/migrations | `alembic/versions/0001…0008` | IMPLEMENTED | `test_migrations.py`, invariant tests; fresh backend suite PASS | Alembic, PostgreSQL; SQLite test compatibility | High | NO DEPLOYED DB EVIDENCE | Tests and local sessions | Schema code exists; this audit did not inspect a production HFM DB |
| CAP-005 | API | `api/health.py`, `api/system.py` | PARTIAL | `test_health.py`, `test_system.py`, `test_app.py` | FastAPI | Low | OPERABLE FOR PROBES ONLY | Operators/developers | Only `/health`, `/ready`, `/version`, `/live`, `/config`; no domain CRUD/public API |
| CAP-006 | RBAC | No auth/RBAC modules or routes | ABSENT | None | None | N/A | NOT_READY | None | Phase 1 placeholder documents do not count |
| CAP-007 | Identity/authentication | No User, credential, token, session, login, or auth middleware | ABSENT | None | None | N/A | NOT_READY | None | `created_by` is an opaque provenance string, not identity |
| CAP-008 | Library | No library page, route, API, or service | ABSENT | None | None | N/A | NOT_READY | None | Work/Edition/Version models are domain primitives, not a Library product |
| CAP-009 | Reader | No reader page, route, or passage API | ABSENT | None | None | N/A | NOT_READY | None | Passage model/repository alone is not a reader |
| CAP-010 | Workspace | No research project/session/workspace implementation | ABSENT | None | None | N/A | NOT_READY | None | HFB workspace is not present in HFM |
| CAP-011 | Search | No search endpoint, service, index, or UI | ABSENT | None | None | N/A | NOT_READY | None | Elasticsearch is conditional/documentary only |
| CAP-012 | Evidence | `models/evidence.py`, `repositories/evidence.py`, migration `0004` | IMPLEMENTED | Evidence model/provenance/hash/taint/repository tests | SQLAlchemy; SourceRef or Passage anchor | High canonical coupling | DATA_LAYER_ONLY | Assertions/Citations via repositories/tests | Enforces anchored evidence and taint states; no API/UI |
| CAP-013 | SourceRef | `models/source_ref.py`, `repositories/source_ref.py`, locator utility, migration `0001` | IMPLEMENTED | SourceRef, locator, provenance tests | Source; structured locator fields | High canonical coupling | DATA_LAYER_ONLY | Evidence/tests | Addressability exists; no ingestion/admission UI |
| CAP-014 | Citation | `models/citation.py`, `repositories/citation.py`, migrations `0006/0007` | IMPLEMENTED | Citation model/evidence/reproducibility/withdrawal tests | Assertion, Version, Passage, Evidence | High canonical coupling | DATA_LAYER_ONLY | Tests | Targets Assertion and supports pinned Version/Passage; no public citation surface |
| CAP-015 | Versioning/ancient text lineage | `models/{work,edition,version,chapter,passage}.py`, corresponding repositories, migration `0003` | IMPLEMENTED | CD-2 lineage, cross-work, protected-field, citation reproducibility tests | SQLAlchemy | High canonical coupling | DATA_LAYER_ONLY | Citation/tests | Work→Edition→Version and Chapter/Passage structures exist; no content loaded |
| CAP-016 | Corpus/data holdings | `completion/migration.py`, `scripts/core_completion/dry_run.py`, `artifacts/audit/hfm-phase0.4-core-completion.json` | PARTIAL | `test_core_completion.py`; fresh suite PASS | Frozen HFB JSON source for dry-run only | Medium; import tooling isolated from runtime | NOT_IMPORTED | Dry-run evidence only | 96 source-universe records assessed; production import explicitly not performed; HFM persistent corpus NONE |
| CAP-017 | Knowledge graph | No general graph model/service/query API/UI | ABSENT | None | None | N/A | NOT_READY | None | Relational Assertions/EventRelations are usable primitives, not an implemented KG product |
| CAP-018 | AI | No model provider, prompt runtime, RAG, embedding, or AI API | ABSENT | None | None | N/A | NOT_READY | None | AI appears only in architecture discussion; no dependency installed by HFM package |
| CAP-019 | Export | No report, citation export, file generation, or download endpoint | ABSENT | None | None | N/A | NOT_READY | None | Data can be queried in tests only |
| CAP-020 | Audit | `core/logging.py`, request-ID middleware; source withdrawal/taint fields | PARTIAL | Logging, request-ID, error tests | Python logging | Low for operational logs; high for provenance state | NOT AUDIT-GRADE | Developers/operators | No immutable user action audit, admin viewer, or publication audit trail |
| CAP-021 | Admin | No admin API, page, user management, health dashboard, or content workflow | ABSENT | None | None | N/A | NOT_READY | None | `/config` is public system info, not admin |
| CAP-022 | Testing/quality gates | Backend tests + frontend tests and lint/type/build config | IMPLEMENTED | Fresh: backend 235 tests, Ruff, strict mypy; frontend 24 tests, lint, typecheck, build all exit 0 | pytest, Ruff, mypy, Vitest, ESLint, vue-tsc, Vite | Medium | STRONG FOUNDATION; PRODUCT COVERAGE ABSENT | Engineering | Tests cover skeleton/core, not the absent product surfaces |
| CAP-023 | Deployment | `infra/README.md`, `.env.example`; Uvicorn entrypoint | DOCUMENT_ONLY | Build succeeds; no deploy/runtime probe in this audit | PostgreSQL planned; no Docker/K8s manifests in HFM baseline | Medium | NOT_READY | Developers | HFB deployment assets are not HFM deployment assets |
| CAP-024 | Observability | `core/logging.py`, request IDs, health/readiness endpoints | PARTIAL | Logging/request-ID/health tests | stdlib logging, FastAPI | Low | BASIC ONLY | Operators/developers | No metrics, tracing, alerting, dashboards, SLOs, or external collector |

## 3. Database/domain facts

Implemented canonical families include Entity, Person, Institution, Work, Edition, Version, Chapter, Passage, Source, SourceRef, Evidence, Assertion, Citation, Event, and EventRelation. The schema includes constraints and repository guards for identity, lineage, cross-work consistency, evidence anchoring, assertion coexistence, protected fields, citation reproducibility, source withdrawal, and event/assertion subject matching.

This is a substantial **canonical data foundation**, not an implemented visitor/researcher/student application.

## 4. Fresh candidate-bound verification

The Git baseline was exported into `/private/tmp`; the dirty working tree was not used as the source tree.

```text
Backend pytest:    PASS (exit 0; 235 tests by progress count)
Backend Ruff:      PASS (exit 0)
Backend mypy:      PASS (exit 0; 101 source files)
Frontend ESLint:   PASS (exit 0)
Frontend typecheck:PASS (exit 0)
Frontend Vitest:   PASS (exit 0; 8 files / 24 tests)
Frontend build:    PASS (exit 0; 30 modules)
```

One existing Starlette/httpx deprecation warning remains non-blocking. No browser, deployed PostgreSQL, production API, production import, or public portal runtime was tested because those HFM product capabilities do not exist at this baseline.

## 5. Inventory conclusion

HFM owns a tested repository skeleton and a frozen canonical research-domain persistence layer. It does **not** yet own the two-layer product, public portal, research workbench, identity/RBAC, content ingestion/publication, search, Library, Reader, Workspace, Knowledge Graph, AI, Export, or Admin capabilities.
