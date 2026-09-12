# HFM 本地部署与测试指导手册

本手册用于：**本地部署、本地演示、客户验收测试**。它不是生产部署手册。

## 1. 本手册用途

- 在一台满足要求的本地机器上，从交付代码启动真实的 HFM 系统；
- 初始化本地数据库并导入演示数据；
- 验证系统健康与版本；
- 按清单手动测试已交付功能（公共门户、研究工作台、首页后台数据）；
- 运行仓库既有自动化测试。

手册中每条命令都已在本地实际执行验证；请按「执行位置」在对应目录/终端中
运行。

## 2. 交付版本

- `DELIVERED_COMMIT = c9dd6ad2eb7e6ae4ae90adcb9cfbc7f44ffcfbd5`（权威软件 /
  当前交付基线）
- `CDP_BASELINE = c0c272f3cddf4e38efa3c3770caa7bcfcd2119dd`（客户交付文档
  基线）

区别：交付基线是被冻结的软件功能版本；交付文档基线在其后追加了客户交付包
文档。两者都只涉及仓库内同一套软件；本地部署请检出交付代码并保持工作区
干净。正式生产部署不在本手册范围。

## 3. 环境要求（已在本机验证）

| 项 | 本手册验证值 | 说明 |
| --- | --- | --- |
| 操作系统 | macOS（Darwin） | 其他平台请按等价方式调整命令 |
| Python | 3.12+（本仓库虚拟环境使用 Python 3.13） | 需能创建/使用虚拟环境 |
| Node.js | 仓库声明 pnpm 10.33.2（本机验证 Node 26.x 可运行） | 前端工具链 |
| 包管理器 | pnpm 10.33.2 | 仓库已锁定 |
| PostgreSQL | 16.x（本机 Homebrew 版） | 需要可用的本地实例 |
| 端口 | 8000（后端）、5173（前端） | 启动前请确认未被占用 |

## 4. 首次部署

在一个终端（下面称为 **终端 C**）执行准备命令：

```bash
# 确认代码位置与干净工作区
cd <仓库根目录>
git status --short          # 应为空
git log -1 --oneline        # 记录交付提交
```

### 4.1 后端依赖

仓库内已提供后端虚拟环境（`apps/backend/.venv`）时可直接使用；否则新建：

```bash
cd apps/backend
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## 5. 数据库初始化

仍在 **终端 C**：

```bash
# 1) 创建本地数据库（名称可自定；请勿改动其他数据库）
createdb hfm_ldct_demo

# 2) 执行迁移（<用户> 替换为你的本地 PostgreSQL 账号）
cd apps/backend
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_ldct_demo" \
  .venv/bin/python -m alembic -c alembic.ini upgrade head

# 3) 核对迁移结果
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_ldct_demo" \
  .venv/bin/python -m alembic -c alembic.ini current
# 预期输出：0014 (head)

HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_ldct_demo" \
  .venv/bin/python -m alembic -c alembic.ini heads
# 预期输出：仅一行 0014 (head)（单一迁移头）
```

### 演示数据边界

执行仓库演示数据导入（用于本地演示与验收；**不代表完整生产内容**）：

```bash
cd apps/backend
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_ldct_demo" \
  PYTHONPATH=src .venv/bin/python scripts/bootstrap_recovery.py
# 预期输出：RECOVERY_BOOTSTRAP=CREATED entity_id=person-huangfu-mi
```

该步骤创建一个公开人物演示记录，用于人物页/搜索等功能的本地演示。

## 6. 启动后端

新开一个终端（**终端 A**）：

```bash
cd <仓库根目录>/apps/backend
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_ldct_demo" \
  .venv/bin/python -m uvicorn hfm.main:app --host 127.0.0.1 --port 8000
```

预期输出：日志中出现 `Application startup complete` 与
`Uvicorn running on http://127.0.0.1:8000`。

## 7. 验证后端

在 **终端 C** 执行：

```bash
curl -s http://127.0.0.1:8000/health
# 预期：{"status":"ok","service":"hfm"}

curl -s http://127.0.0.1:8000/ready
# 预期：{"status":"ready","service":"hfm"}

curl -s http://127.0.0.1:8000/live
# 预期：JSON，含 success=true

curl -s http://127.0.0.1:8000/version
# 预期：JSON，含 success=true 与 version 字段
```

## 8. 启动前端

新开一个终端（**终端 B**）：

```bash
cd <仓库根目录>
pnpm install --frozen-lockfile   # 首次部署时执行；之后可跳过
pnpm dev
```

预期输出：Vite 提示 `Local: http://localhost:5173/`。在浏览器打开
`http://localhost:5173`，页面标题为「皇甫谧人文数字平台」。

## 9. 系统功能测试

浏览器地址 = `http://localhost:5173`。逐项执行并记录结果。

| TEST_ID | SURFACE | ACTION | EXPECTED_RESULT | PASS_CRITERION |
| --- | --- | --- | --- | --- |
| S1 | 首页 | 打开 `/` | 平台标题与八段内容渲染 | 页面可滚动浏览、无报错 |
| S2 | 首页搜索 | 输入「皇甫谧」并回车 | 跳转 `/search?q=皇甫谧` 并显示结果 | URL 与结果条目 |
| S3 | 人物 | 打开 `/persons/person-huangfu-mi` | 人物资料页面渲染 | 页面显示人物名 |
| S4 | 甲乙经 | 打开 `/jiayi` | 古籍相关内容页渲染 | 页面渲染 |
| S5 | 非遗 | 打开 `/heritage` | 非遗档案页渲染 | 页面渲染 |
| S6 | 搜索空态 | 输入不存在的词并回车 | 显示「未找到匹配…的结果」 | 页面文案与清除关键词入口 |
| S7 | 读者/文献面 | 打开 `/reader/houlun` | 文献阅读/整理页可打开 | 页面渲染 |

记录浏览器控制台：无未捕获错误；无意外接口失败。

## 10. 研究工作台测试

研究工作台需要**已授权研究账户**（由维护人员开通并提供给你）。以下
`<用户名>`、`<密码>` 为占位，请使用你获得的账户。

| 步骤 | 动作 | 预期结果 |
| --- | --- | --- |
| 1 登录 | 打开 `/login`，输入研究账户用户名密码，点「登录」 | 进入「研究工作台」 |
| 2 写入项目 | 「我的研究 → 新增项目」：填项目标题（必填）与描述 →「创建项目」 | 提示「项目已创建」，列表可见 |
| 3 回看（重启后） | 刷新/重新登录后进入研究工作台 | 项目仍在列表（数据库持久化） |
| 4 写入笔记 | 「我的笔记 → 新增笔记」：填内容（必填）→「创建笔记」 | 提示「笔记已创建」，列表可见 |
| 5 回看（重启后） | 刷新/重新登录后进入研究工作台 | 笔记仍在列表 |

> 说明：当前前端登录会话保存在内存中；刷新页面或关闭浏览器后需重新登录，
> 但项目与笔记已保存于数据库，重新登录后仍可读取（这正是持久化回看步骤）。

未登录直接访问 `/research` 会被引导到登录页（权限边界）。

## 11. 首页后端数据验证

在首页正常打开、后端可用时：

1. 打开 `http://localhost:5173/`；
2. 打开浏览器开发者工具 → 网络，刷新页面；
3. 确认存在对 `/api/v1/public/home` 的请求且返回 200 JSON；
4. 首页正常渲染八段内容；当演示数据包含公开人物时，「研究导航」板块会显示
   对应公开人物上线信息；
5. 若后端不可用，首页应仍能渲染既有内容而不报错（安全降级）。

## 12. 自动化测试

在对应目录执行（**终端 C**）：

```bash
# 后端全量测试
cd <仓库根目录>/apps/backend
PYTHONPATH=src .venv/bin/python -m pytest -q
# 预期：全部通过，无失败/错误

# 前端单元测试 / 类型检查 / 构建
cd <仓库根目录>/apps/frontend
pnpm vitest run
pnpm vue-tsc --noEmit
pnpm build
```

浏览器端到端测试需要后端与前端正在运行（本手册第 6、8 节已启动），从
`apps/frontend` 执行既有 Playwright 用例。

## 13. 停止系统

| 终端 | 操作 | 结果 |
| --- | --- | --- |
| 终端 B（前端） | 按 `Ctrl-C` | Vite 进程退出，命令行返回 |
| 终端 A（后端） | 按 `Ctrl-C` | Uvicorn 进程退出，命令行返回 |

## 14. 重启系统

### 后端重启

1. 在终端 A 按 `Ctrl-C` 停止后端；
2. 确认命令行已返回；
3. 再次执行第 6 节的后端启动命令；
4. 验证：`curl -s http://127.0.0.1:8000/health` 返回 `{"status":"ok",...}`。

### 前端重启

1. 在终端 B 按 `Ctrl-C` 停止前端；
2. 再次执行第 8 节的前端启动命令；
3. 验证：浏览器打开 `http://localhost:5173` 正常渲染首页。

## 15. 常见问题

- **页面打不开**：确认后端运行于 8000、前端运行于 5173，端口未被占用。
- **后端报数据库连接错误**：确认 PostgreSQL 已启动、连接串中账号/库名正确。
- **登录后刷新回到登录页**：属当前设计（登录态保存在内存）；重新登录即可，
  数据不会丢失。
- **搜索无结果**：尝试更常见关键词（如「皇甫谧」）；无结果提示为预期行为。
- 其他问题请联系系统维护人员。

## 16. 验收结果记录表

| TEST_ID | 结果（通过/不通过） | 备注 |
| --- | --- | --- |
| S1–S7 功能 | … | … |
| 研究工作台写读回看 | … | … |
| 首页后端数据 | … | … |
| 自动化测试 | … | … |
| 重启验证 | … | … |

## 17. 当前交付边界

- 软件发布门（GATE_A）= PASS
- 客户交付门（GATE_B）= PASS
- 内容完成门（GATE_C）= OPEN（内容建设继续独立推进）
- R0 = 0、R1 = 0（当前交付已完成）
- R2（文献全文深加工、知识对象深度数字化）= 后续
- R3（后台/媒体运营工具）= 后续
- 生产部署 = 后续

本手册不代表生产部署手册；生产部署需要另行安排。
