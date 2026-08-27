# HFB → HFM Asset Reuse Matrix

Status: **Frozen** · Version: 1.0 · Date: 2026-08-27 · Phase 0 — Repository Bootstrap & HFB Asset Reuse Planning

> 依据：`docs/audit/HFD-PHASE0-BASELINE-AUDIT.md` v1.1（HEAD `2d98b610`）+ `docs/audit/HFD-PHASE0-DOMAIN-MAP.md` v1.1。
> 判定词汇：REUSE（原样复用）/ EXTEND（复用并扩展）/ ADAPT（适配改造）/ DEPRECATE（废弃）/ NEW（新建）。
> 迁移策略：Port（携带证据链移植代码）/ Port + Extend（移植后扩展）/ Port + Build（移植并新建缺失部分）/ Deprecate（排除）/ Build（全新构建）。
> 变更规则：冻结后任何裁决变更须经 ADR 裁决并升版；跨切 NEW 缺口（G1 医学合规 / G2 匿名门户 / G3 发布快照 / G4 非遗媒体）登记于 BASELINE-AUDIT §14 Gap Register。

| Domain / Capability | HFB Source | Verdict | HFM Target | Migration Strategy | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Authentication | `api/v1/auth.py` + `middleware/auth.py`（JWT Bearer+cookie 双通道，token_version 吊销） | REUSE | Identity & Access | Port | BASELINE §6/§11.2；G2 匿名 Visitor 绑定 = NEW | Frozen v1.0 |
| RBAC | `db/seed_rbac.py`（8 角色 × 21 资源 + source_admission 五动作） | REUSE / EXTEND | Identity & Access | Port + Extend（G7 SoD 强制、公开 Visitor 角色） | BASELINE §6/§11.1；G7 | Frozen v1.0 |
| Person | `models/person.py`（domain_status/anchor_path）+ `repositories/person.py`（verified 过滤）+ PersonIntro 展览 | REUSE | Domain + Public Portal | Port + Extend（公开人物档案） | DOMAIN-MAP §1.1；BASELINE §7 | Frozen v1.0 |
| Ancient Text | `models/bibliographic.py`（FRBR）+ Book/ClassicalVersion/Version/Chapter/Passage/Sentence/Token/Variant + TEI | REUSE | Domain + Public Portal | Port + Extend（公开古籍阅读） | DOMAIN-MAP §1.2/§1.4；BASELINE §7 | Frozen v1.0 |
| Source | `models/source_admission.py`（三级状态机）+ append-only 审计 | REUSE | Evidence & Provenance | Port | DOMAIN-MAP §1.3；BASELINE §5 | Frozen v1.0 |
| Evidence | `models/academic_evidence.py`（Level 1-4 + taint）+ `candidate_publish_uow.py` | REUSE | Evidence & Provenance | Port | DOMAIN-MAP §1.3；BASELINE §5/§6 | Frozen v1.0 |
| Citation | `models/academic_evidence.py`（Citation target→evidence）+ `citation_persistence.py`（撤回引用拒绝） | REUSE | Evidence & Provenance | Port | DOMAIN-MAP §1.3；BASELINE §6 | Frozen v1.0 |
| Reader | `pages/reader/ReaderPage.vue`（研究版）+ `repositories/document.py`（P4 过滤） | REUSE / EXTEND | Public Portal | Port + Extend（匿名公开版阅读器） | BASELINE §6/§7；G2 | Frozen v1.0 |
| Library | `pages/library/*` + P4 过滤 | REUSE | Public Portal | Port | BASELINE §6 | Frozen v1.0 |
| Search | `api/v1/search.py` + `services/search_service.py`（P4 fail-closed） | REUSE | Shared Infrastructure | Port | BASELINE §6 | Frozen v1.0 |
| Knowledge | `pages/knowledge/*` + `api/v4/visualization.py` | REUSE | Content & Research Workbench | Port | BASELINE §6 | Frozen v1.0 |
| Reports | `pages/reports/*` + `export_run_markdown` | REUSE | Content & Research Workbench | Port | BASELINE §6 | Frozen v1.0 |
| Export | markdown 导出（REUSE）；PDF/打印（无） | REUSE / NEW | Content & Research Workbench | Port + Build（PDF/打印 + G9 免责保留） | BASELINE §6；G9 | Frozen v1.0 |
| AI Copilot | `services/ai_service.py`（Evidence-Gated，EVIDENCE_GATE_REFUSAL） | REUSE / EXTEND | Content & Research Workbench | Port + Extend（医学护栏 G8） | BASELINE §8/§13；DOMAIN-MAP §1.7；G8 | Frozen v1.0 |
| Media | 静态 JSON 引用（`PersonIntroView.vue:389-404`，2 mp4 无后端登记） | DEPRECATE / NEW | Media & Rights | Deprecate + Build（G4 全链治理，模板复用 hfmzl candidate/admission 链） | BASELINE §9/§13；DOMAIN-MAP §1.6；G4/G13 | Frozen v1.0 |
| Publication | 无 PublishedRepresentation / PublicationSnapshot（仅 ProductionPromotion 哈希快照） | NEW | Publication | Build（§8.3 快照分类学先行；G3/G5） | BASELINE §8.3/§10；DOMAIN-MAP §1.9/§1.13；G3/G5 | Frozen v1.0 |
| Rights | `models/document.py` copyright_status/license_type/authorization_basis（字段 REUSE）；媒体权利全链（无） | REUSE / NEW | Media & Rights | Port + Build（媒体权利治理 G13） | BASELINE §9.1/§13；DOMAIN-MAP §1.10；G13 | Frozen v1.0 |
| Teaching | `api/v4/education.py`（分级 + evidence 强制，需登录） | EXTEND | Teaching | Port + Extend（公开化 + 医学合规 G1/G8） | BASELINE §7/§13；G1/G8 | Frozen v1.0 |
