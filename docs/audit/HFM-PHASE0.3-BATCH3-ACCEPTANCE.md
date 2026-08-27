# HFM Phase 0.3 — Batch 3 Migration Acceptance（Codex Independent）

Date: 2026-08-27 (Asia/Shanghai)
Mode: READ-ONLY acceptance — 未修改 HFM 源码/测试/配置/依赖/Git 历史/HFB；仅新增本报告（未提交、未推送）

## 1. Final Verdict

**PASS**（0 P0 / 0 P1 / 0 P2 / 2 P3）

## 2. Repository Baseline

| Item | Value | Verdict |
| --- | --- | --- |
| Branch | `main` | CONFIRMED |
| HEAD | `b3207edd16ed2478f6229fdc15dfafb21aec83ad` | CONFIRMED |
| origin/main | 同一 SHA | CONFIRMED |
| Working tree | clean（验收前） | CONFIRMED |
| merge-base（b5388af..b3207ed） | `b5388af0490f9d7b3e14b9a6f1f1ccff781e81c1` | CONFIRMED（ancestry 成立） |
| 历史链 | b3207ed → b5388af → c2f61d5 → 45e6cc1 → 981030f → 5ba7662 | CONFIRMED（无改写） |
| 记录身份 | `b3207ed` = Batch 3 implementation candidate；`5d8466a` = first acceptance-record correction commit；**Current Acceptance Record: this commit** | CONFIRMED |

## 3. Inventory Verification

独立统计 `HFM-PHASE0.3-BATCH3-INVENTORY.md` 候选表（11 行）：

```text
Candidates Audited: 11
PORT: 2
ADAPT: 1
REFERENCE_ONLY: 1
DEFER: 4
REJECT: 3
```

**INVENTORY COUNTS: CONFIRMED**（inventory 内部一致：11 = 2+1+1+4+3；Migrated Assets 3 = PORT 2 + ADAPT 1）。

**P2-1（CLOSED）**：实施报告 §3 汇总行「DEFER 5」已修正为「DEFER 4」（提交 `5d8466a`），与 inventory（权威）一致；计数笔误，不影响任何迁移内容。

## 4. Asset-by-Asset Verification

| Asset | HFM Target | Mode | Source @03755b5 | Domain Semantics | HFM Tests | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| API error normalization | `apps/frontend/src/utils/errors.ts` | PORT | `apps/frontend/src/api/client.ts`（ApiErrorDetail/getApiErrorDetail 部分）EXISTS | 无（纯 status/message 提取） | `errors.spec.ts`（4 tests） | CONFIRMED |
| Vitest matchMedia polyfill | `apps/frontend/src/test-setup.ts` | PORT | `apps/frontend/src/test-setup.ts` EXISTS | 无（test infra only；setupFiles 已接线，不影响生产 bundle） | `test-setup.spec.ts`（1 test） | CONFIRMED |
| System info endpoints | `apps/backend/src/hfm/api/system.py` | ADAPT | `apps/backend/app/api/version.py` EXISTS | 无（/version /live /config 通用系统信息） | `test_system.py`（3 tests） | CONFIRMED |

## 5. Coupling Verification

| Asset | Pi Coupling | Codex Coupling | Verdict |
| --- | --- | --- | --- |
| errors.ts | LOW | **LOW**（纯函数，无领域引用；无 hfb/research/evidence/citation/publication/workspace 上下文命中） | CONFIRMED |
| test-setup.ts | LOW | **LOW**（纯测试基建，无业务语义/领域 fixture） | CONFIRMED |
| system.py | LOW | **LOW**（settings 依赖已剥离为模块常量；HFM namespace） | CONFIRMED |

**HIGH Coupling Assets Migrated: 0**

## 6. Provenance

| Asset | HFB Source | HFM Target | Mode | Provenance | Verdict |
| --- | --- | --- | --- | --- | --- |
| errors.ts | `client.ts` @`03755b5` | `src/utils/errors.ts` | PORT | 文件头记录 + inventory 映射 | CONFIRMED |
| test-setup.ts | `test-setup.ts` @`03755b5` | `src/test-setup.ts` | PORT | 文件头记录 + inventory 映射 | CONFIRMED |
| system.py | `version.py` @`03755b5` | `src/hfm/api/system.py` | ADAPT | 文件头记录 + inventory 映射 + ADAPT 明细 | CONFIRMED |

## 7. Core Domain Audit

diff `b5388af..b3207ed` 新增代码扫描：无 Person/Book/Edition/Version/Chapter/Passage/Assertion/Source/Evidence/Citation/Publication/MediaAsset/Rights/Teaching/ResearchSession/Workspace/Workflow/User/Role/Permission 实现（唯一「version」命中为 /version 应用版本端点与测试，非领域 Version）。

**Core Domain Migration: NO**

## 8. Phase 1 Boundary

未实现 G1/G2/G3/G4/G7；`/config`/`/live` 为通用系统信息端点，非 G2 public access 实现（无匿名内容访问语义）。

**Phase 1 Business Coding: NO**

## 9. HFB Independence

无 `from hfb` / `import hfb` / `../hfb` / `/Users/likeming/Sites/hfb` / `@hfb/`；无 symlink、无 submodule、无 local path dependency、无 runtime HTTP 调用 HFB（文档 provenance 除外）。

**Permanent HFB Runtime Dependency: NO**

## 10. Dependency Audit

`package.json` / `pnpm-lock.yaml` / `pnpm-workspace.yaml` / `apps/frontend/package.json` / `apps/backend/pyproject.toml` diff：**无变化**。

**New Dependencies: 0**

## 11. Quality Gates（独立运行）

| Gate | Fresh Result | Count |
| --- | --- | --- |
| Ruff | PASS | — |
| Ruff format | PASS | 24 files |
| mypy --strict | PASS | 24 source files |
| pytest | PASS | **26 passed** |
| ESLint | PASS | — |
| Prettier | PASS | — |
| vue-tsc | PASS | — |
| Vitest | PASS | **24 passed** / 8 files |
| Build | PASS | — |

## 12. Test Quality

- `errors.spec.ts`：正常提取、detail 回退、message 回退、null/非对象边界 — 实质行为测试，无 assert True。
- `test-setup.spec.ts`：通过 `window.matchMedia()` 调用验证 stub 形状（matches/media/addEventListener），非仅存在性检查。
- `test_system.py`：/version 结构与字段、/live 载荷、**/config 白名单子集断言（安全测试）** — 覆盖 §8.4 安全边界。

## 13. Batch 1 / Batch 2 Regression

- diff `--name-status`：无任何 Batch 1/2 测试文件被修改（无掩盖回归）。
- 全量 pytest 26（含 B1 hashing/logging/response/errors、B2 pagination）、Vitest 24（含 B1 misc/smoke、B2 types/useToast/useTheme/useFocusTrap）全绿。
- request-id 冒烟正常（§14）。

**Batch 1 Regression: PASS · Batch 2 Regression: PASS**

## 14. Runtime Smoke（独立启动）

| Endpoint | Result | 关键结构 |
| --- | --- | --- |
| /health | 200 | `{"status":"ok","service":"hfm"}` |
| /ready | 200 | `{"status":"ready","service":"hfm"}` |
| /version | 200 | envelope + `data.version=0.1.0 / environment / project=HFM` |
| /live | 200 | envelope + `data.alive=true` |
| /config | 200 | envelope + `data={project_name,version,environment}` |
| X-Request-ID | PASS | `x-request-id: ed4a8a25-…` |
| Frontend | 200 @ **5499**（实际端口） | `<title>HFM · 皇甫谧人文数字平台</title>` |

## 15. System Endpoint Safety

- /version：仅 app 版本/环境/项目名；无 HFB 路径、无敏感环境变量。
- /live：轻量 liveness，零外部依赖。
- /config：仅白名单 `{project_name, version, environment}`；无 secrets/password/token/DB 凭据/含凭据 URL/API key。
- /health、/ready、/live 语义区分：health=基础服务健康、ready=readiness（骨架零外部依赖，轻量合理）、live=liveness（`alive` 载荷）— 非重复副本。
- **/config Secret Exposure: NO**

## 16. Git Hygiene

`git diff --check b5388af..b3207ed`：PASS。无未提交 `.env`/secrets/caches/node_modules/virtualenv/build 产物。

## 17. Findings

| Level | Count | Detail |
| --- | --- | --- |
| P0 | 0 | — |
| P1 | 0 | — |
| P2 | 0 | — |
| P3 | 2 | ① Starlette/httpx deprecation warning（既有，OPEN/NON-BLOCKING，未恶化、未升级依赖"顺手解决"）；② /ready 骨架期轻量（无外部依赖，符合 Frozen 条件性基础设施原则，Phase 1 引入 infra 时完善） |

**Previous P2: CLOSED**

- 实施报告 §3「DEFER 5」与 inventory「DEFER 4」不符（计数笔误）已修正（`5d8466a`：实施报告计数修正 + 验收报告入库）。
- Remaining Acceptance Corrections: **NONE**

## 18. Batch 3 Ruling

**HFM PHASE 0.3 BATCH 3: ACCEPTED**

- Previous P2: **CLOSED** — The acceptance report is now tracked and the DEFER count is corrected to 4.
- Remaining Acceptance Corrections: **NONE**
- Batch 4 不在本轮授权范围内。
