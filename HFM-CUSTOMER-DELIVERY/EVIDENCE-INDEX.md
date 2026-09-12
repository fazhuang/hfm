# EVIDENCE-INDEX — 历史验收证据与可复现核验

本索引明确区分两类证据：

- **当前交付事实（随交付包可复核）**：源码与测试文件的仓库路径 + 可复现
  命令。这是验收时应优先重跑的证据。
- **历史验收归档（仓库内已提交的验收文档）**：指出具体归档文件；其中记录
  的是对应里程碑的既有验收结论，不属于本交付包新增主张。

## 1. 当前交付事实（源码 + 测试，可复现）

| 能力 | 实现文件（仓库路径） | 证据测试文件 | 复现命令 |
| --- | --- | --- | --- |
| 登录/鉴权（研究端） | `apps/backend/src/hfm/api/v1/phase1.py`（auth 路由）· `apps/backend/src/hfm/phase1/auth.py` | `apps/backend/tests/test_phase1_auth_contract.py` | 见 `TEST-COMMAND-INDEX.md`（后端测试） |
| 研究项目与笔记创建/回看 | `apps/backend/src/hfm/phase1/research_workspace.py` · `apps/backend/src/hfm/api/v1/phase1.py`（projects/notes 路由） | `apps/backend/tests/test_phase1_research_workspace.py` | 同上 |
| 研究工作台前端在线创建 | `apps/frontend/src/views/research/ResearchHomeView.vue` · `apps/frontend/src/components/research/ResearchWorkspacePanel.vue` · `apps/frontend/src/services/research.ts` | `apps/frontend/src/__tests__/rem01_research_workspace.spec.ts` | `pnpm vitest run`（前端） |
| 首页后台公开数据接入与降级 | `apps/frontend/src/views/HomeView.vue` · `apps/frontend/src/composables/useHomePublicData.ts` · `apps/frontend/src/data/homePublicEnrichment.ts` | `apps/frontend/src/__tests__/rem02_home_public.spec.ts` | `pnpm vitest run`（前端） |
| 公共门户后端接口 | `apps/backend/src/hfm/api/v1/phase1.py`（public 路由）· `apps/backend/src/hfm/phase1/portal.py` | `apps/backend/tests/test_phase1_portal.py` | 见 `TEST-COMMAND-INDEX.md` |

浏览器走查按 `DEMO-GUIDE.md` 步骤执行并记录结果（作为过程证据保存于验收
记录，随验收方归档）。

## 2. 历史验收归档（仓库内既有文档，指向具体文件）

| 能力/里程碑 | 归档文件（仓库路径） | 说明 |
| --- | --- | --- |
| 研究端登录/权限/研究工作台后端（P1-12 里程碑） | `docs/audit/HFM-PHASE1-FRONTIER6-P1-12-IMPLEMENTATION.md` | 该里程碑实现与验收说明 |
| 公共门户 UI 与响应式/无障碍验收 | `docs/design/HFM-UI-FINAL-ACCEPTANCE-EVIDENCE.md` | 界面验收记录 |
| 公共端界面证据截图 | `docs/audit/evidence/`（对应界面验收截图） | 视觉验收制品 |
| 运行/运维/恢复契约 | `docs/operations/ND1-RELEASE-QUALIFICATION.md` | 发布、备份、恢复、回滚说明 |
| 用户与学者操作手册 | `docs/user-guide/HFM-USER-AND-SCHOLAR-GUIDE.md` | 随本次交付提交 |

## 3. 说明

- 本交付包对应的功能验收记录（REM-01/02/03 阶段）由验收方独立执行并留存；
  仓库内以第 1 节「源码 + 测试文件 + 可复现命令」作为可复核证据，避免以
  会话日志代替归档。
- 临时数据库与临时日志已清理，不进入交付数据；如需复核某项结论，请按
  第 1 节命令重跑。
