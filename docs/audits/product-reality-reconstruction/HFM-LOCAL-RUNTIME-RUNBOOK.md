# HFM-LOCAL-RUNTIME-RUNBOOK.md — 本地运行与开发者启动手册

本文档为从未接触过 HFM 的工程师提供在新环境从零启动完整系统的标准操作步骤。

---

## 1. 运行前置要求 (Prerequisites)

- **Node.js**: >= 20.x
- **pnpm**: >= 9.x
- **Python**: >= 3.12 (推荐 3.13)
- **PostgreSQL**: >= 15 (开发测试亦可临时使用 SQLite)

---

## 2. 依赖安装

### 前端依赖
```bash
# 在仓库根目录执行
pnpm install
```

### 后端依赖
```bash
cd apps/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 3. 环境变量配置 (Environment)

复制开发环境样例并确认参数：
```bash
# 后端配置
export HFM_ENV=development
export HFM_DATABASE_URL="postgresql+asyncpg://hfb:change-me@127.0.0.1:5432/hfm"
# 如果没有外部 Postgres，测试时可指定本地 SQLite:
# export HFM_DATABASE_URL="sqlite+aiosqlite:///$(pwd)/local_dev.db"
export HFM_TOKEN_SECRET="hfm-dev-secret-key-32-characters-minimum"
```

---

## 4. 数据库初始化与迁移 (Migration)

```bash
cd apps/backend
source .venv/bin/activate
alembic upgrade head
```

初始化系统角色与初始管理员（可选但推荐）：
```bash
python scripts/bootstrap_recovery.py
```

---

## 5. 启动服务 (Start Services)

### 5.1 启动后端 API (Port 8000)
```bash
cd apps/backend
source .venv/bin/activate
uvicorn hfm.main:app --host 127.0.0.1 --port 8000 --reload
```
- 健康检查：访问 `http://127.0.0.1:8000/health` (返回 `{"status":"ok","service":"hfm"}`)
- 系统版本：访问 `http://127.0.0.1:8000/version`

### 5.2 启动前端应用 (Port 5173)
在另一个终端：
```bash
# 根目录下
pnpm --filter frontend dev
```
- 前端入口：访问 `http://localhost:5173`

---

## 6. 验证系统运行 (Verification)

1. 打开浏览器访问 `http://localhost:5173`，应完整展现 8 个板块的“皇甫谧人文数字平台”首页。
2. 访问 `http://localhost:5173/jiayi`，查看《针灸甲乙经》128 篇目录及古籍版本。
3. 访问 `http://localhost:5173/search?q=皇甫谧`，检查检索功能是否响应。
4. 访问 `http://localhost:5173/login`，测试登录认证守卫。

---

## 7. 服务关闭与清理 (Shutdown)

- 在启动终端直接按 `Ctrl + C` 退出 uvicorn 与 vite 进程即可。
