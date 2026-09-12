# 02 — 安装与启动（可直接执行）

> 本页命令基于仓库真实工具链；占位符 `…` 处按你的环境填写。命令在当前
> 交付形态（本机运行）下使用，不涉及公网生产部署。

## 0. 前置

- PostgreSQL 已启动（`pg_isready` 通过）。
- Python（仓库声明版本）与 pnpm（仓库声明版本）可用。
- 已检出交付代码，工作区干净。

## 1. 创建数据库并迁移

```bash
# 1) 创建演示数据库（名称可自定）
createdb hfm_delivery_demo

# 2) 安装后端依赖（在仓库 apps/backend 下使用项目虚拟环境，或新建）：
cd apps/backend
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# 3) 执行数据库迁移到交付头（0014）
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_delivery_demo" \
  .venv/bin/python -m alembic -c alembic.ini upgrade head

# 4) 核对迁移结果（应输出 0014 (head)）
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_delivery_demo" \
  .venv/bin/python -m alembic -c alembic.ini current
```

说明：`<用户>` 为你的本地 PostgreSQL 账号；如无本地账号请先创建或使用已有
账号，并确保可连接。

## 2. 导入公开演示内容（可选但建议）

交付的公共示例数据（含公开人物内容）由维护脚本导入：

```bash
cd apps/backend
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_delivery_demo" \
  PYTHONPATH=src .venv/bin/python scripts/bootstrap_recovery.py
```

## 3. 安装前端依赖

```bash
cd <仓库根目录>
pnpm install --frozen-lockfile
```

## 4. 启动后端

```bash
cd apps/backend
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/hfm_delivery_demo" \
  .venv/bin/python -m uvicorn hfm.main:app --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/version
```

两个接口都应返回 JSON（含 success=true）。

## 5. 启动前端

另开终端：

```bash
cd <仓库根目录>
pnpm dev
```

默认访问 <http://localhost:5173> 。（如端口被占用，Vite 会提示并可使用
`pnpm dev --port <端口>` 指定。）

## 6. 研究演示账户

研究工作台需要**已授权研究账户**。账户由维护人员按仓库运维说明（
`docs/operations/`）创建并授予研究权限；本包不提供固定账号或密码。验收
研究流程前，请先由维护人员开通一个研究账户并提供给你。

## 7. 常见启动问题

- 后端无法连接数据库：检查 PostgreSQL 是否启动、连接串是否正确。
- 前端打不开后端数据：确认后端运行在 8000 端口且前端代理指向它（本地
  开发环境默认已配置）。
- 更多排查见仓库运维说明与《用户与学者操作指南》常见问题。
