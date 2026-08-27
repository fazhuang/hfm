# HFM Phase 0.4 — CD-0 Implementation Report

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-0
性质：Core Domain 第一批实施（Frozen DAG CD-0 唯一准绳）

## 1. Starting Baseline

- **Core Domain Contract Baseline**：`366df69715613022326eb7a3c06ae7f145ebacb9`（HFM HEAD = origin/main，working tree clean）

## 2. HFB Source Snapshot

- **HFB Source Snapshot（固定只读）**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`

## 3. Frozen CD-0 Scope

- 详见 `docs/migration/hfb/HFM-PHASE0.4-CD0-IMPLEMENTATION-SCOPE.md`（**CD-0 SCOPE: CONFIRMED**）
- 对象：Source（身份+rights 元数据）/ SourceRef / Institution + Stable Identifier / Locator 值对象 + DB 基座 + 迁移
- 明确排除：SourceAdmission 状态机、CD-1+ 对象、Auth/RBAC、Phase 1、前端、业务 API、HFB 数据导入（NOT PERFORMED）

## 4. Traceability Matrix

- 见 Scope 文档（8 项 Requirement → Contract Source → HFB Source → HFM Target → Implementation → Test）；所有生产代码可映射

## 5. Implemented Objects

```text
apps/backend/src/hfm/core/identifiers.py      # uuid7 + is_valid_uuid（I5）
apps/backend/src/hfm/core/locator.py          # Locator 值对象（结构化定位）
apps/backend/src/hfm/core/config.py           # 最小环境配置（DATABASE_URL/HFM_ENV）
apps/backend/src/hfm/db/base.py               # Base + TimestampMixin + BaseModel（__abstract__）
apps/backend/src/hfm/db/session.py            # async engine/session
apps/backend/src/hfm/models/source.py         # Source（不可变 source_key + rights 元数据）
apps/backend/src/hfm/models/source_ref.py     # SourceRef（source FK + 结构化 locator）
apps/backend/src/hfm/models/institution.py    # Institution（type/status + CHECK 约束）
apps/backend/src/hfm/repositories/{base,source,source_ref,institution}.py
apps/backend/alembic/                        # alembic.ini + env.py + script.py.mako + versions/0001
```

## 6. REUSE Assets

- `uuid7`（HFB `db/base.py` 纯函数 → `core/identifiers.py`）— 通用纯函数，行为一致
- `SourceRef` 字段（title/author/edition_info/url — CA-020）→ `models/source_ref.py` 基础字段
- `Institution` 字段与枚举（CA-005）→ `models/institution.py`（name/type/location/description/status）

## 7. EXTEND Assets

- `SourceRef`：增加结构化 `locator` JSON 列（Locator 值对象）+ 必需 `source_id` FK（I1 锚定）

## 8. ADAPT Assets

- `Source`（CA-019）：保留身份+rights 元数据（source_key/source_type/source_uri/rights_basis/allowed_scope/authorization_basis/legacy_source_key）；**移除**三级准入状态机与审核工作流（治理层）
- `Base/TimestampMixin`（HFB `db/base.py`）：保留 DeclarativeBase + 时间戳；**移除** SoftDeleteMixin（CD-0 范围不需要）
- `BaseRepository`（HFB `repositories/base.py`，B 系列 DEFER 项现按需落地）：保留 create/get_by_id/update/delete/count；**移除** soft-delete 与跨字段检索
- 配置（settings 模式）：环境变量直读，无 pydantic-settings 依赖

## 9. NEW Assets

- `Locator` 值对象（结构化定位 — HFB 仅有字符串 page_location）
- `is_valid_uuid` 校验、`create_idempotent` 幂等创建
- Alembic 迁移基础设施 + `0001_cd0_foundation`（三表 + 约束 + 索引）

## 10. Database Changes

```text
tables: sources / source_refs / institutions
constraints: uq_sources_source_key（UNIQUE）、source_refs.source_id FK RESTRICT、
             ck_institutions_type / ck_institutions_status（CHECK）
indexes: ix_source_refs_source_id
```

## 11. Migration Changes

- `alembic/versions/0001_cd0_foundation.py`（revision 0001，upgrade/downgrade）
- 验证：fresh upgrade PASS、downgrade base 删表 PASS、replay 幂等 PASS（test_migrations 3 tests）

## 12. Data Import

```text
HFB DATA IMPORT:
NOT PERFORMED
```

（Frozen CD-0 未明确包含数据导入执行；data dependency「source identity 导出」记录为后续授权输入，按 HFM-CORE-DATA-MIGRATION-STRATEGY dry-run 流程另行执行。）

## 13. APIs

```text
API Changes:
0
```

（Frozen CD-0 未列 API；未新增业务 endpoint。）

## 14. Tests

- `test_identifiers.py`（4）：格式/版本 nibble/变体、时间有序、唯一性、非法校验
- `test_locator.py`（6）：构造、to_locator_string、空定位、JSON 往返、from_mapping、相等性
- `test_source_model.py`（4）：幂等创建、无静默覆盖、重复键拒绝、get_by_key
- `test_source_ref_model.py`（4）：必需 Source（I1）、锚定解析、RESTRICT 级联、标题非空
- `test_institution_model.py`（3）：构造、非法类型 CHECK 拒绝、CRUD
- `test_repositories.py`（5）：CRUD 往返、update 缺失、泛型实例化、幂等、**不可变字段拒绝**（update 拒绝 source_key/id；声明级断言）
- `test_invariants.py`（3）：I1 溯源种子、I5 稳定身份幂等、I4 无状态变更
- `test_migrations.py`（3）：fresh upgrade、downgrade、replay 幂等
- `test_source_model.py`（5）：**模型级 source_key 直接变更拒绝**（validates 守卫）+ 幂等创建、无静默覆盖、重复键拒绝、get_by_key

## 15. Invariant Tests

- I1（SourceRef 必锚定 Source）、I4（重复导入不覆盖）、I5（source_key 唯一/幂等）专项测试通过；I2/I3/I6 由本批设计不阻塞（无相关对象/无 HFB 依赖，I6 由独立性审计覆盖）

## 16. Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format | PASS（50 files） |
| mypy --strict | PASS（48 source files，零 ignore/exemption） |
| pytest | **57 passed**（前 26 + CD-0 31） |
| ESLint | PASS |
| Prettier | PASS |
| vue-tsc | PASS |
| Vitest | **24 passed / 8 files**（无前端变更，回归） |
| Build | PASS |

## 17. Runtime Regression

- /health /ready /version /live /config 全部 200；X-Request-ID 正常；/config 无敏感（无 password/token/secret/DATABASE_URL 命中）

## 18. HFB Independence

- 源码/配置扫描：无 `Sites/hfb` / `../hfb` / `from hfb` / `import hfb` / `@hfb/` / `03755b57`（docs provenance 除外）
- 无 symlink / submodule / local path dependency / runtime HTTP / 共用 DB

**Permanent HFB Runtime Dependency: NO**

## 19. Contract Deviations

```text
Contract Deviations:
0
```

（实现过程中未发现 Frozen Contract 无法实现或事实冲突。）

## 19.1 P1 修正记录（Codex CD-0 Acceptance BLOCK → 修复）

- **P1**：`Source.source_key` 声明不可变，但 `BaseRepository.update()` 允许 `setattr` 修改稳定身份键。
- **修复（双层防护）**：
  - `BaseModel.immutable_fields`（默认 `{"id"}`）+ `Source.immutable_fields = {"id", "source_key"}`；
  - `BaseRepository.update()` 对 immutable 字段显式 `ValueError` 拒绝；
  - `Source` 模型 `@validates("source_key")` 守卫 — 持久化后直接属性赋值同样拒绝（I5）。
- **新增测试**：`test_update_rejects_immutable_fields`、`test_immutable_fields_declared_on_model`、`test_source_key_direct_mutation_rejected`（pytest 57 → **60 passed**）。

## 20. Phase 1 Boundary

- 未实现 G1/G2/G3/G4/G7；无 Auth/RBAC/权限迁移；无前端；无 /public/* /publish /withdraw /release

## 21. Scope Closure

```text
CD-0 Frozen Scope Items:
8（Scope 文档 Traceability Matrix 行数）

Implemented:
8

Deferred:
0

Unauthorized Additions:
0
```
