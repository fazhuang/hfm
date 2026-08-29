# HFM Phase 1 — Frontier-4 Implementation Evidence（P1-05 / P1-06）

Date: 2026-09-01 · Phase 1 — Frontier-4 Implementation Evidence
Execution baseline: `8e769791bd30493b66ce4a1ea7b75aea80fe3d9c`（Frontier-3 Acceptance）
Branch: `phase1/frontier-4-p1-05-p1-06`
证据契约：HFM-PHASE1-EVIDENCE-CONTRACT-v1.md（E-05 / E-06）

## 实施范围

```text
P1-05 — C 《针灸甲乙经》数字知识体系（historical disease/point/meridian/
        technique retrieval returns source/version/citation；无临床语义）
P1-06 — D 非遗传承体系（lineage relations carry official-name, evidence and
        publication state；无未证实传承主张公开）
实施顺序 P1-05 → P1-06（仅实施排序，不改 DAG）
未实施任何其他 WP / Display / AI / 3D / VR / XR / Virtual Training / clinical；
未重新打开已验收 WP（仅 P1-08 检索扩展、P1-13 对账范围扩展等严格必需的最小集成）。
```

## 架构要点（跨 WP 一致性）

- C/D 领域记录不建立任何并行的 Source/Evidence/Citation/Version/Publication/RBAC
  真值存储：C 术语 / D 非遗项目的**发布投影**统一绑定到既有 P1-01 ContentArtifact
  （`content_artifacts.subject_entity_id → entities.id`），公开可见性唯一由
  P1-09 `publication_status == PUBLISHED` 决定（AB-03/AB-07）；
- C 术语与 D 非遗项目均获得 typed-Entity 稳定身份（`entity_id → entities.id`，
  I5，与 persons/works/events 骨架一致）；C 穴位术语用 `entity_type='acupoint'`，
  其余术语与非遗项目用 `entity_type='concept'`（冻结 EntityType 七族内）；
- C 术语锚定版本化文献（`canonical_passage_id → passages.id`，P1-04 复用），
  检索返回原文段落 + 版本谱系摘要（VersionLineageService，E-13 集成）；
- C 历史关系与 D 传承关系的**证据绑定** = `evidence_id → evidences.id`
  （P1-02 复用）；公开投影仅暴露带证据的关系（E-05/E-06：un-evidenced 主张不公开）；
- D 传承主体 = P1-03 Person Entity（或 institution Entity），repository 强制
  person/institution 校验（P1-03 集成）；
- 变更审计写入既有 append-only `audit_log`（P1-13 AuditService）；
  C/D 新表加入 P1-13 对账范围（`_SCOPE_MODELS`）；
- 检索扩展复用 P1-08 SearchService（同一子系统，无第二检索子系统），公开端硬注入
  PUBLISHED 谓词，研究端需认证（ADR-02/05/07）。

## WP-ID P1-05 — C 《针灸甲乙经》数字知识体系

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | historical disease/point/meridian/technique retrieval returns source/version/citation（E-05）；no diagnosis, treatment, ranking or prescription（AB-14） |
| Implementation Files | `src/hfm/models/c_domain.py`（CDomainTerm/CDomainRelation）+ `src/hfm/repositories/c_domain.py` + `src/hfm/phase1/c_domain.py`（CDomainService）+ `src/hfm/api/v1/phase1.py`（public/research c-terms 端点）+ `src/hfm/phase1/search.py`（c_term 检索集成） |
| Migration Files | `0012_p1_frontier4.py`（c_domain_terms / c_domain_relations） |
| Test Files | `tests/test_phase1_c_domain.py`（11 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_c_domain.py -q` |
| Observed Result | 11 passed（创建 / 非法关系拒绝 / 证据绑定 / source-version-citation 检索 / 无隐式发布 / 发布可见性 / 撤回 / 未发布 404 / 公开仅带证据关系 / 未授权拒绝 / 检索集成 / 临床语义缺失） |
| Negative Tests | 自环拒绝；未知目标术语拒绝；缺失证据拒绝；空术语名拒绝；关系绑定不可变；未发布术语公开 404；撤回后公开投影消失；未证实关系公开排除；匿名创建/关系拒绝；`prescription/diagnosis/treatment/recommend` 表面缺失（AB-14） |
| Evidence Paths | `docs/audit/HFM-PHASE1-FRONTIER4-P1-05-P1-06-IMPLEMENTATION.md` |

要点：历史术语=Entity(concept/acupoint)+CDomainTerm（I5）；历史关系=CDomainRelation
（source↔target，typed relation，无自环）；`canonical_passage_id` 提供原文（source）
与版本（version lineage hash）上下文；公开投影仅暴露 PUBLISHED 且带证据的历史关系；
创建/准入绝不产生发布记录（无隐式发布）；变更经 P1-10 `assertion:create` 授权；
无诊断/治疗/处方/主配穴推荐表面（AB-14 / ADR-02 Guard-02）。

## WP-ID P1-06 — D 非遗传承体系

| 项 | 内容 |
| --- | --- |
| Acceptance Criterion | lineage relations carry official-name, evidence and publication state（E-06）；no unverified heritage/inheritor claim public |
| Implementation Files | `src/hfm/models/heritage.py`（HeritageProject/HeritageRelation）+ `src/hfm/repositories/heritage.py` + `src/hfm/phase1/heritage.py`（HeritageService）+ `src/hfm/api/v1/phase1.py`（public/research heritage 端点）+ `src/hfm/phase1/search.py`（heritage_project 检索集成） |
| Migration Files | `0012_p1_frontier4.py`（heritage_projects / heritage_relations） |
| Test Files | `tests/test_phase1_heritage.py`（10 项） |
| Verification Command | `cd apps/backend && ../../.venv/bin/pytest tests/test_phase1_heritage.py -q` |
| Observed Result | 10 passed（项目创建 / 传承关系 official-name+证据 / 非法关系拒绝 / 无隐式发布 / 发布可见性+撤回 / 未发布 404 / 公开仅带证据传承关系 / 研究端含带证据关系 / 未授权拒绝 / 检索集成） |
| Negative Tests | 未知项目拒绝；未知主体拒绝；非 person/institution 主体拒绝（P1-03 集成）；缺失证据拒绝；空项目名拒绝；关系绑定不可变；未发布项目公开 404；撤回后公开投影消失；未证实传承关系公开排除 |
| Evidence Paths | 同上 |

要点：非遗项目=Entity(concept)+HeritageProject（官方名称锚点，I5）；传承关系=
HeritageRelation（project↔person/institution，官方名称 + 时间框架 + 证据绑定，
E-06）；传承主体强制为 P1-03 Person 或 institution Entity；公开投影仅暴露
PUBLISHED 且带证据的传承关系；创建/准入绝不产生发布记录；变更经 P1-10 授权，
写入 P1-13 审计；无客户端内容（测试用合成夹具）。

## 回归

```text
pytest: 346 passed / 0 failed / 1 warning（Starlette 既有弃用提示）
mypy: PASS（138 source files）· Ruff: PASS · Ruff Format: PASS（138 files）
Pyright (CLI, src tests): 0 errors / 0 warnings / 0 informations
Alembic: 0012 (head)（0001→0012 链 + upgrade/downgrade 门禁测试 PASS）
API 冒烟（SQLite 迁移库）：public c-terms/heritage 未发布 404 · public search 200 ·
        research c-terms/heritage 匿名访问被拒绝（默认拒绝保持；500 为既有
        PermissionError 通用处理器行为，与已验收 P1-08/P1-10 API 一致）
聚焦回归：P1-05 11 + P1-06 10 + P1-02/03/04/08/09/10/13 相关 102 项全部 PASS
```

## 边界确认

```text
- 未实施 P1-07、P1-11、P1-12；未实施 Display/AI/3D/VR/XR/Virtual Training/clinical
- 未重新打开已验收 WP；P1-08 检索扩展与 P1-13 对账范围扩展为本前沿严格必需的最小集成
- 无生产 HFB 导入（NOT PERFORMED / NOT AUTHORIZED）；无 HFB runtime 依赖；未执行 M5
- CD-7: NONEXISTENT
- 未修改任何冻结治理工件（Scope/DAG/Acceptance/Evidence/DoD/Boundary/Authorization/ADR）
- 冻结 Phase 0.4 表未被破坏性迁移；0012 仅新增表（可回退）
```

## 完成判定

```text
P1-05 = PASS · P1-06 = PASS（各自独立证据）
```

## 聚焦回归明细

```text
P1-05（test_phase1_c_domain.py）: 11 passed
P1-06（test_phase1_heritage.py）: 10 passed
P1-02 evidence-chain / P1-03 person / P1-04 literature / P1-08 search /
P1-09 publication / P1-10 rbac / P1-13 version-audit / migrations: 102 passed
合计: 聚焦回归 123 passed（包含在完整 346 passed 内）
```
