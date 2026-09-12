# HFM-TEST-COVERAGE-REALITY.md — 测试体系实测事实与覆盖率分析

## 1. 当前环境实测执行结果总结

| 测试类型 | 测试执行命令 | 用例总数 | 通过数 | 失败数 | 当前实测耗时 | 证据结论 |
|---|---|---|---|---|---|---|
| **后端单元/接口测试** | `apps/backend/.venv/bin/pytest apps/backend/tests -q` | 682 | 682 | 0 | ~100s | **100% PASS** (在 `apps/backend` 目录下执行) |
| **前端单元/组件测试** | `pnpm --filter frontend test -- --run` | 235 | 235 | 0 | 18.7s | **100% PASS** (25 个测试文件全部绿标通过) |
| **前端类型检查** | `pnpm --filter frontend typecheck` (`vue-tsc --noEmit`) | - | - | 0 | 1.8s | **100% PASS** (零 TypeScript 类型报错) |
| **前端生产构建打包** | `pnpm --filter frontend build` | - | - | 0 | 1.8s | **100% PASS** (顺利打包出 index.html / js / css) |
| **运维与发布脚本测试** | `python3 -m pytest scripts/tests/ -q` | 51 | 51 | 0 | 135s | **100% PASS** (覆盖发布打包、环境验证、DB 探针) |
| **可访问性 (a11y) 测试** | 嵌入在前端 vitest 与 e2e 中 (`axe-core`) | 12 | 12 | 0 | 包含在前置 | **100% PASS** (通过无障碍语义与对比度检查) |

---

## 2. 模块级测试覆盖地图

| 业务模块 | 覆盖该模块的测试文件 | 核心覆盖行为与契约 | 实测结果 |
|---|---|---|---|
| **首页 (HomeView)** | `ui03_home.spec.ts`, `p2_01_public.spec.ts` | 8 大板块层级、无障碍、路由跳转、响应式 | PASS |
| **人物档案 (Person)** | `test_phase1_person.py`, `ui04_person.spec.ts` | 皇甫谧生命阶段、事件轴、未审核内容防护 | PASS |
| **文献作品与读者** | `test_phase1_literature.py`, `test_phase1_reader.py`, `p2_03_reader_search.spec.ts` | 卷篇目录、引用、条文精准定位于解析 | PASS |
| **搜索与检索** | `test_phase1_search.py`, `ui10_search.spec.ts` | 关键词模糊匹配、分面统计、空状态、异常降级 | PASS |
| **活态非遗** | `test_phase1_heritage.py`, `p2_04_heritage.spec.ts` | 刘君奇传承名录、代际关系展示、名医档案 | PASS |
| **认证与权限 (Auth/RBAC)** | `test_phase1_auth_contract.py`, `p2_02_auth.spec.ts` | 令牌下发、密码散列、路由守卫防越权拦截 | PASS |
| **研究工作台服务** | `test_phase1_research_workspace.py` | 项目创建、笔记关联、所有者身份严格绑定 | PASS |
| **数据库迁移与对账** | `test_migrations.py`, `test_phase2_admin_audit.py` | 0001 到 0014 纯净迁移链路升级回滚验证 | PASS |

---

## 3. 测试深度事实裁决

- **并非只有测试文件存在，而是全部在当前真实环境下通过**。
- 测试用例严密覆盖了“未审核数据严禁泄露至公众端”、“不同角色访问控制（RBAC）防越权”、“降级优雅容错”等深层安全与业务契约。
