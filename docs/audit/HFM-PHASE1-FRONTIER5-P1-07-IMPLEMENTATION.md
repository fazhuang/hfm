# HFM Phase 1 — Frontier-5 Implementation Evidence（P1-07）

Date: 2026-09-01 · Phase 1 — Frontier-5 Implementation Evidence
Execution baseline: `311e24c610dd7c7325cada51b23cfc3c4ed1bcea`（Frontier-4 Acceptance）
Branch: `phase1/frontier-5-p1-07`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-07）

## 实施范围

```text
P1-07 — P1-READER 版本化典籍阅读器（versioned source reader）
目标（Scope Register P1-READER）：Locate and study source text
未实施 P1-11 / P1-12（下游工作包，均等待 P1-07 正式验收）
未实施 Display / AI / 3D / VR / XR / Virtual Training / clinical
未重新打开已验收 WP；P1-07 不改变既有验收字节的语义
```

## 架构要点（跨 WP 一致性）

- 阅读器 = **只读投影**，不引入任何新表/新列（当前 Alembic head 保持 `0012`）；
  消费既有规范表：Work/Edition/Version/Chapter/Passage（P1-04）、
  Evidence/SourceRef/Source（P1-02）、Citation（P1-02/05）、
  CDomainTerm（P1-05 canonical passage 锚）、ContentArtifact +
  PublicationRecord（P1-09 发布态）——无重复真值存储（AB-03/AB-04/AB-07）；
- **定位可复现性（E-07）**：阅读器返回的 `locator` 恒为从 Passage FK
  谱系推导的规范定位符（`LiteratureService.passage_locator`，P1-04 复用），
  输入定位符中的实体 ID（work/edition/version/chapter/passage）与谱系
  交叉校验，不匹配即拒绝（fail-closed，防伪造定位）；
- **公开/研究边界（ADR-05）**：
  - `GET /api/v1/public/reader/resolve` — 匿名，仅 PUBLISHED 投影；
    草稿、未发布、撤回版本一律 404（不泄露存在性）；
  - `GET /api/v1/research/reader/resolve` — 强制认证（P1-10 RBAC），
    返回完整证据链上下文（Source→SourceRef→Evidence + Citation target）；
- **公开可读谓词**（三路并集，任一满足且 pinned Version 未撤回）：
  (a) Work 谱系 Entity 绑定 PUBLISHED ContentArtifact（P1-04 投影）；
  (b) 该 Passage 被绑定 PUBLISHED artifact 的 Evidence 引用（P1-08
      公开检索谓词——公开可检索片段必须可读）；
  (c) 该 Passage 是 PUBLISHED C 域术语的 canonical passage（P1-05 投影）；
- 阅读器输出**不做关系遍历**（无跨域穿越）、无任何临床语义表面（AB-14）；
  引用（citation）仅暴露定位引用装置（quote_text），不暴露内部
  证据描述/污损状态/来源 URI（公开端）；研究端才提供富证据链；
- 无 HFB runtime 依赖；无生产导入（NOT PERFORMED / NOT AUTHORIZED）。

## WP-ID P1-07 — 版本化典籍阅读器（Versioned Source Reader）

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | passage locator reproducibly opens source context and citation（E-07）；no reader access to unauthorized draft |
| Implementation Files | `src/hfm/phase1/reader.py`（ReaderService）+ `src/hfm/api/v1/phase1.py`（public/research reader 端点）+ `src/hfm/core/locator.py`（`from_locator_string` 定位符解析，STRICTLY_REQUIRED_INTEGRATION） |
| Migration Files | 无（0012 保持 single head；阅读器为只读投影，无 schema 变更） |
| Test Files | `tests/test_phase1_reader.py`（13 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_reader.py -q` |
| Observed Result | 13 passed（公开解析=原文+来源+引用上下文 / 定位可复现性 / 定位符往返 / 畸形定位符拒绝 / 谱系不匹配拒绝 / 未发布排除 / 撤回版本排除 / 发布撤回即时隐藏 / RBAC 拒绝 / 研究端富证据链 / P1-05 canonical passage 集成 / 公开证据绑定可读 / 无关系遍历无临床表面） |
| Negative Tests | 畸形定位符失败关闭；locator 无 passage 锚拒绝；未知 key 拒绝；work/edition/version/chapter 谱系不匹配拒绝；未发布 passage 公开 404；撤回版本公开排除；发布撤回后公开投影消失；研究端匿名拒绝；公开端不泄露证据描述/污损/来源 URI/引用 target；无 relations 键（无跨域遍历） |
| Evidence Paths | `docs/audit/HFM-PHASE1-FRONTIER5-P1-07-IMPLEMENTATION.md` |

要点：ReaderService 是 P1-07 的规范读取表面——给定 passage 定位符（或
passage id）返回引文原文（quotation）、来源上下文（Work/Edition/Version
谱系 + lineage digest）、引用上下文（引用该 passage 的 Citation）、
权利显示（authorizing 发布投影的 rights/provenance）与发布状态；
公开谓词与 P1-08 检索/ P1-04 文献/ P1-05 C 域投影一致，撤回即时阻断
（ADR-05 Guard-03）；研究端富证据链仅在认证后暴露。

## Acceptance Criterion → Evidence 映射

| Criterion | 实现文件 | 迁移 | 正向测试 | 负向测试 | 命令 | 观测结果 |
| --- | --- | --- | --- | --- | --- | --- |
| E-07 定位可复现性（same locator → same version/passage） | `phase1/reader.py`（`resolve_public`/`_anchor`） | 无 | `test_locator_reproducibility_same_locator_same_passage`、`test_locator_round_trip_and_canonical_derivation` | `test_ancestry_mismatch_rejected`（错误 version/work ID 拒绝） | `pytest tests/test_phase1_reader.py -q` | 13 passed；同一定位符两次解析逐字段相等；canonical 定位符往返一致 |
| 引文原文（quotation）保留 | `phase1/reader.py`（`_view`） | 无 | `test_public_resolve_opens_source_and_citation` | — | 同上 | `quotation == passage.content_text` |
| 来源上下文（source context: Work/Edition/Version + lineage） | `phase1/reader.py`（`_view` + VersionLineageService 复用） | 无 | `test_public_resolve_opens_source_and_citation` | — | 同上 | work/edition/version/chapter 字段与谱系 hash 均在 |
| 引用上下文（citation context） | `phase1/reader.py`（`_citations`） | 无 | `test_public_resolve_opens_source_and_citation`、`test_research_reader_richer_evidence_context` | 公开端不泄露 `target_assertion_id`/`note` | 同上 | 公开端仅 citation_id+quote_text；研究端含 target/note |
| 权利显示（rights display） | `phase1/reader.py`（`_rights_display`） | 无 | `test_public_resolve_opens_source_and_citation` | — | 同上 | rights_status=PUBLISHED 投影绑定值 |
| 无未授权草稿访问（negative） | `phase1/reader.py`（`_passage_public`） | 无 | `test_public_evidence_bound_passage_readable` | `test_unpublished_passage_not_public`、`test_withdrawn_version_excluded_publicly`、`test_publication_withdrawal_hides_passage`、`test_malformed_locator_fails_closed_public` | 同上 | 未发布/撤回/撤回发布均公开 404 |
| RBAC（P1-10） | `api/v1/phase1.py`（`require_authenticated` + service principal 校验） | 无 | `test_research_reader_richer_evidence_context` | `test_research_reader_requires_authentication` | 同上 | 匿名研究端拒绝（PermissionError） |
| P1-04 集成（literature passages） | `phase1/reader.py`（passage_locator 复用） | 无 | `test_public_resolve_opens_source_and_citation` | `test_ancestry_mismatch_rejected` | 同上 | 定位符谱系一致 |
| P1-05 集成（passage/section trace） | `phase1/reader.py`（`_authorizing_entities`） | 无 | `test_c_domain_canonical_passage_public_via_published_term` | — | 同上 | PUBLISHED C 术语的 canonical passage 公开可读 |
| P1-02 集成（citation/source context） | `phase1/reader.py`（`_citations`/`_evidence`） | 无 | `test_public_evidence_bound_passage_readable` | — | 同上 | Evidence 绑定 PUBLISHED artifact 的 passage 公开可读 |
| AB-14 无临床语义 / 无关系遍历 | `phase1/reader.py`（输出键集封闭） | 无 | `test_no_relation_traversal_no_clinical_surface` | 同左 | 同上 | 视图键集有界，无 relations/诊断/处方表面 |

## 回归

```text
pytest: 359 passed / 0 failed（此前 346 + P1-07 新增 13）
mypy: PASS（140 source files）· 命令: cd apps/backend && ../../.venv/bin/mypy src tests
Ruff: PASS · Ruff Format: PASS（153 files already formatted）
Pyright（CLI, src+tests）: 0 errors / 0 warnings / 0 informations
Alembic: 0012 (head) 保持 single head；down_revision=0011；0001→0012 链有效；
        upgrade/downgrade 门禁测试 PASS（20 项，无 schema 变更）
聚焦回归（P1-02/04/05/08/09/10/13 + heritage + governance 相关）: 82 passed
API 冒烟（TestClient）: 公开端畸形 locator → 404（fail-closed）；
        研究端匿名访问被拒绝（默认拒绝保持；PermissionError 通用处理器
        行为与已验收 P1-08/P1-10 API 一致）
```

## 边界确认

```text
- 未实施 P1-11、P1-12；未实施 Display/AI/3D/VR/XR/Virtual Training/clinical
- 未重新打开已验收 WP；P1-07 仅新增只读 reader 表面 + 定位符解析
  （STRICTLY_REQUIRED_INTEGRATION），不改动既有验收字节语义
- 无生产 HFB 导入（NOT PERFORMED / NOT AUTHORIZED）；无 HFB runtime 依赖
- CD-7: NONEXISTENT
- 未修改任何冻结治理工件（Scope/DAG/Acceptance/Evidence/DoD/Boundary/Authorization/ADR）
- 无 schema 变更（head 保持 0012）——阅读器为只读投影
```

## 完成判定

```text
P1-07 = PASS（实施验证；正式 ACCEPTED 判定权属 Codex）
```

## 聚焦回归明细

```text
P1-07（test_phase1_reader.py）: 13 passed
migration gates（test_migrations.py）: 20 passed
P1-02 evidence-chain / P1-04 literature / P1-05 c-domain / P1-08 search /
P1-09 publication / P1-10 rbac / P1-13 version-audit / P1-06 heritage /
P1-07 governance 相关: 82 passed
合计: 聚焦回归 115 passed（包含在完整 359 passed 内）
```
