# DELIVERY-MANIFEST — 交付清单

| 字段 | 值 |
| --- | --- |
| DELIVERY_PACKAGE | 皇甫谧人文数字平台 — 客户交付包（CDP-01） |
| DELIVERY_DATE | 2026-09-07 |
| DELIVERY_BRANCH | recovery/hfm-foundation |
| DELIVERED_COMMIT | 0704118722f61f0922a05b480943fb69bbb8fda1（软件最终实现提交） |
| PACKAGE_COMMIT | 本交付包所在提交（提交后随交付报告记录实际 SHA） |
| PACKAGE_PATH | `HFM-CUSTOMER-DELIVERY/` |
| PACKAGE_MD_FILES | 13 个 Markdown 文件（见文末索引） |
| DOCUMENTATION_ONLY | 是（不含产品代码/API/数据库/迁移/UI/infra/scripts 改动） |
| MIGRATION_HEAD | 0014（单一迁移链头） |
| 交付形态 | 本地可运行软件形态（非公网生产部署） |

## 门与状态（以验收方冻结事实为准）

| 项目 | 状态 |
| --- | --- |
| SOFTWARE_COMPLETE（软件交付范围） | YES |
| CURRENT_DELIVERY_SCOPE_COMPLETE | YES |
| CUSTOMER_DELIVERY_READY | YES |
| CONTENT_COMPLETE | NO |
| GATE_A_SOFTWARE_RELEASE | PASS |
| GATE_B_CUSTOMER_DELIVERY | PASS |
| GATE_C_CONTENT_COMPLETION | OPEN |
| R0_REMAINING | 0 |
| R1_REMAINING | 0 |
| REM-01（研究工作台在线创建项目与笔记） | CLOSED（已验收并随交付提交） |
| REM-02（首页公开数据接入与降级） | CLOSED（已验收并随交付提交） |
| REM-03（用户与学者操作指南） | CLOSED（已随交付提交；独立文档验收记录见验收方） |
| 后续内容深加工（文献全文深度处理、知识对象深度数字化） | 后续内容建设范围（R2 类，不在本包） |
| 后台/媒体运营工具 | 后续运营能力（R3 类，不在本包） |
| 公网生产部署 | 后续部署阶段 |

## 工作包状态（软件交付范围）

| 工作包 | 内容 |
| --- | --- |
| 公共门户 | 首页/人物/《针灸甲乙经》/其言/非遗/搜索 |
| 研究工作台在线创建 | 研究项目与笔记的新增界面 + 真实 API + 数据库持久化与回看 |
| 首页后台数据接入 | 首页读取后台公开数据 + 安全降级 |
| 用户与学者操作指南 | 终端用户手册 |
| 客户交付包 | 本目录文档 |

## 本包文档索引（13 个文件）

| 路径 | 用途 |
| --- | --- |
| `DELIVERY-MANIFEST.md` | 本清单 |
| `NOTICE.md` | 许可证事实披露 |
| `00-START-HERE/README.md` | 从哪里开始读、按什么顺序验收 |
| `00-START-HERE/ACCEPTANCE-CHECKLIST.md` | 独立验收清单 |
| `01-DELIVERY-OVERVIEW.md` | 交付内容总览 |
| `02-INSTALLATION/README.md` | 可执行的安装、迁移、启动与健康检查命令 |
| `03-RUNBOOK/README.md` | 运行/停止/备份/恢复/回滚要点与真实命令 |
| `03-DELIVERED-SCOPE.md` | 已交付功能清单 |
| `04-BOUNDARIES-AND-NEXT.md` | 数据/接口边界与后续范围 |
| `05-TECHNICAL-HANDOVER.md` | 接收技术团队交接说明 |
| `DEMO-GUIDE.md` | 确定性演示步骤 |
| `TEST-COMMAND-INDEX.md` | 测试命令索引 |
| `EVIDENCE-INDEX.md` | 历史证据与可复现核验索引 |
