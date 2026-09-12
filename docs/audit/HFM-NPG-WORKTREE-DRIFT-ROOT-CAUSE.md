# HFM NPG — Worktree Drift Root Cause（取证报告）

Status: FORENSIC REPORT · Date: 2026-08-29 · Branch: `governance/next-phase-authorization`
目标：`scripts/core_completion/dry_run.py`（Phase 0.4 CORE-COMPLETION 工具文件）
模式：只读取证 + 受控复现；本报告不实施修复。

## Observed drift

```text
文件: scripts/core_completion/dry_run.py
变化: 18 insertions / 5 deletions（纯折行重排）
每次出现逐字节相同（同一 SHA-256）
出现时机: 每次对文件执行 restore/写入后的 agent_end
```

## Current patch SHA-256

```text
8db7da3185efc220fdb568e91d638c81ee0b22d1a4dcd73ee774091b0ae01613
（../hfm-npg-recurring-dry-run-drift.patch，2431 bytes）
```

## Same as previous drift

```text
YES — IDENTICAL_TO_PREVIOUS
（与 ../hfm-pre-npg-r1-dry-run-local-drift.patch 逐字节一致；
与 NPG-R1.1 保存的 patch 一致；三次独立捕获同一产物）
```

## Semantic

```text
FORMAT_ONLY — 无语义变化
转换类型: Ruff 折行重排（line wrapping）
具体重排:
  - EXPECTED_SOURCE_SHA256 常量换行（含 108 字符行 → 88 列折行）
  - load_source_records 函数签名换行
  - apply_target 元组展开换行
  - argparse add_argument 换行
  - print 调用换行
提交版本 max line = 100（apps/backend 配置 line-length 100）
漂移版本 max line = 88（ruff 默认 line-length 88）
```

## Reproducing trigger

```text
NOT_REPRODUCED BY CLI COMMANDS

受控复现矩阵（每命令后立即 git status + git diff）:
  [1] restore 后立即状态        → CLEAN
  [2] pytest --collect-only     → CLEAN
  [3] ruff check（无 --fix）    → CLEAN
  [4] mypy                      → CLEAN
  [5] eslint / prettier --check / vue-tsc → CLEAN

IDE/编辑器检查:
  仓库无 .vscode/settings.json；无 formatOnSave 配置；无编辑器进程
  漂移时间戳与 agent_end 事件吻合，非编辑器活动

实际触发动作（由 pi-lens 自身遥测证明，非本会话 CLI 命令）:
  pi-lens agent_end deferred-format hook
  latency.log:
    formatter_selected: formatter=ruff, reason=smart-default,
      cwd=/Users/likeming/Sites/hfm/scripts/core_completion
    deferred_format_file: changed=true（ruff format 实际改写文件）
    agent_end_deferred_format_start: fileCount 1/5/2（每轮代理结束时排队执行）
```

## Root cause（证据支撑）

```text
机制链:
1. pi-lens 扩展的 agent_end deferred-format hook 在每轮代理结束时，
   对当轮被写入/分派的文件运行 `ruff format`（写模式）。
2. 该 hook 以「文件所在目录」为 cwd 调用 ruff：
   cwd = scripts/core_completion（无 pyproject.toml / ruff.toml / .ruff.toml）
   → ruff 配置发现失败 → 使用默认 line-length 88。
3. 提交版本在提交时以 apps/backend 配置（line-length 100）格式化
   （提交时命令从 apps/backend cwd 执行 → 发现 apps/backend/pyproject.toml）。
   两种配置对同一文件的折行边界不同 → 每次格式化为 88 列版本 → 漂移。
4. 漂移逐字节确定（同一 SHA-256），因为 ruff 默认配置输出是确定性的。

为什么 format.enabled=false 未生效:
  pi-lens 全局配置在扩展启动时加载一次并缓存
  （dist/index.js:106416 `const globalConfig = loadPiLensGlobalConfig()`），
  getLensFlag 使用该缓存 → 会话中途修改 ~/.pi-lens/config.json 不被读取
  → getFlag("no-autoformat") 保持 false → deferred format 照常执行。
  （项目级 .pi-lens.json 按调用读取（mtime 缓存，loadPiLensProjectConfig 每次调用，
  新文件可即时生效），但该文件未被 .gitignore 覆盖。）

为什么仅该文件受影响:
  - scripts/core_completion/dry_run.py → hook cwd=scripts/core_completion → 无配置 → 88 折行 → 漂移
  - apps/backend/src、apps/backend/tests 下文件 → hook cwd 上溯可发现
    apps/backend/pyproject.toml → line-length 100 → 与提交格式一致 → 稳定
```

## Affected scope

```text
仅 scripts/core_completion/dry_run.py（单一文件，工作树级）
提交内容零受影响（HEAD 与父基线该文件逐字节一致 — cmp 验证）
```

## Phase 0.4 semantic impact

```text
NONE — 漂移为纯格式（FORMAT_ONLY，零语义变化）；
提交的候选字节在仓库规范配置（apps/backend ruff format --check）下稳定合规；
漂移从未进入任何提交（每次 restore 后 HEAD 与基线一致）。
```

## Governance impact

```text
影响: 每次 Codex 入口门禁前需先还原工作树（git status 必须 CLEAN）；
多次导致入口门禁 BLOCK（e26598f/7960fb6 期间），已按流程处理。
无治理语义影响；不改变任何冻结决策。
```

## Recommended containment（建议，未实施 — 需另行授权）

```text
规则: 不得为满足格式化器而改动冻结的 Phase 0.4 源文件。
遏制必须在工具/工具链层进行：

P1（首要 — 工具层，无仓库变更）:
  在 pi-lens 扩展启动前确保 ~/.pi-lens/config.json 含 "format": {"enabled": false}
  （该配置仅在扩展启动时读取一次；当前值已设置，但为会话中途写入，
   须重启会话/扩展后生效）。效果: agent_end deferred format 跳过全部文件。

P2（备选 — 项目层，gitignored，即时生效）:
  新建 <repo>/.pi-lens.json = {"format": {"enabled": false}}
  并加入 .gitignore（当前未覆盖 → 需授权修改 .gitignore）。
  项目配置按调用读取 → 会话中途即生效；gitignored → 不弄脏工作树。

P3（防御性 — 配置层，需授权）:
  若未来允许配置文件变更，在 scripts/ 目录放置 ruff.toml
  （line-length 100，与提交格式一致）→ 任何以 scripts/core_completion
  为 cwd 的 ruff 调用均稳定无 diff（双保险，同时防护未来其他格式化器调用）。

P4（流程 — 现状保持）:
  每次 Codex 入口门禁前还原 dry_run.py 至 HEAD（既有实践）；
  审计命令一律使用 check-only 模式（ruff format --check / ruff check 无 --fix）。
```

## Forensic evidence inventory

```text
../hfm-pre-npg-r1-dry-run-local-drift.patch       （8db7da31…，首次保存）
../hfm-npg-r1-1-current-dry-run-drift.patch       （8db7da31…，NPG-R1.1 捕获）
../hfm-npg-recurring-dry-run-drift.patch          （8db7da31…，本次捕获）
~/.pi-lens/latency.log                            （formatter_selected/deferred_format_file 事件）
dist/index.js:106416 / 106417-106420              （全局配置缓存证明）
dist/index.js:7370 loadPiLensProjectConfig        （项目配置按调用读取证明）
```
