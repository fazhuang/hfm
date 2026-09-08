# 03 — 运行手册（RUNBOOK）

> 详细发布/备份/恢复/回滚规范以仓库运维说明为准（`docs/operations/`）。
> 本页仅列接收后可立即执行的要点命令（本机交付形态）。

## 1. 启动与停止

```bash
# 启动后端（前台，另开终端运行前端）
cd apps/backend
HFM_DATABASE_URL="postgresql+asyncpg://<用户>@127.0.0.1:5432/<库名>" \
  .venv/bin/python -m uvicorn hfm.main:app --host 127.0.0.1 --port 8000

# 启动前端
cd <仓库根目录> && pnpm dev

# 停止：对应终端 Ctrl-C
```

## 2. 健康与依赖检查

```bash
# 进程健康
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/version

# 数据库依赖探针（进程存活 + 数据库可达；探针默认读取仓库后端目录，
# 无需 --backend-dir 参数）
bash scripts/database-dependency-probe.sh \
  --api-base http://127.0.0.1:8000 \
  --db-url "postgresql+asyncpg://<用户>@127.0.0.1:5432/<库名>"
```

预期输出含 `PROBE_PROCESS=UP`、`PROBE_DATABASE=OK`、`PROBE_RESULT=PASS`。

## 3. 数据库备份与恢复（要点）

```bash
# 备份（自定义格式）
pg_dump -h 127.0.0.1 -U <用户> -Fc -f /tmp/hfm-backup-$(date +%Y%m%d).dump <库名>

# 恢复到一个新的隔离库（不要在源库上直接覆盖演练）
createdb <新库名>
pg_restore -h 127.0.0.1 -U <用户> -d <新库名> /tmp/hfm-backup-*.dump
```

恢复后核对：迁移版本与交付头一致；研究/笔记数据与公开内容可读取。

## 4. 回滚（要点）

- **应用回滚**：将运行指向回上一版本/上一配置后重新启动并做健康检查。
- **数据库回滚**：不把数据库向下迁移作为常规回滚路径；如需回退数据库状态，
  使用发布前的备份做恢复。
- 回滚后必须重新执行健康检查、依赖探针与关键页面走查。

## 5. 参考文档

| 事项 | 位置 |
| --- | --- |
| 发布/门禁/迁移 | `docs/operations/ND1-RELEASE-QUALIFICATION.md`（发布与迁移章节） |
| 备份/恢复/回滚矩阵 | 同上前述章节 |
| 终端用户操作 | `docs/user-guide/HFM-USER-AND-SCHOLAR-GUIDE.md` |
