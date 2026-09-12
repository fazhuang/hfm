# HFM-PRODUCT-REALITY-BASELINE.md — 产品现实与范围冻结基线

```text
================================================================================
BASELINE_TIMESTAMP : 2026-09-07T23:55:25+08:00
REPO               : /private/tmp/recovery/hfm-foundation
BRANCH             : recovery/hfm-foundation
HEAD               : 1e9336e0b530764da3754de5c1c58650dc38fa60
WORKTREE           : CLEAN
================================================================================

[STATUS DECOMPOSITION MATRIX]
SOFTWARE_FOUNDATION_STATUS        : COMPLETE
PUBLIC_PORTAL_STATUS              : COMPLETE
RESEARCH_WORKSPACE_STATUS         : PARTIAL (前端写UI缺失，后端完全就绪)
ADMIN_WORKFLOW_STATUS             : PARTIAL (审计与对账就绪，审核与上传UI预留)
BACKEND_STATUS                    : COMPLETE (50+ 接口、RBAC、ORM均通过全量测试)
DATABASE_SCHEMA_STATUS            : COMPLETE (0001-0014 纯净迁移链)
DATASET_STATUS                    : COMPLETE (已满足最低可交付数据集 MVDD)
CONTENT_DIGITIZATION_STATUS       : PARTIAL (515篇论文全文与349穴位属持续内容建设)
LOCAL_RUNTIME_STATUS              : COMPLETE (前端/后端秒级启动)
TEST_STATUS                       : COMPLETE (968 个测试全绿通过)
DEPLOYMENT_CONTRACT_STATUS        : COMPLETE (运维脚本、严苛验证器、环境模版齐备)
PRODUCTION_ENVIRONMENT_STATUS     : PENDING  (待客户提供实际物理生产机与域名)
CUSTOMER_DELIVERY_STATUS          : PARTIAL  (待闭合 3 项 R1 级任务即可交付)

--------------------------------------------------------------------------------
SCOPE RESOLUTION VERDICTS
--------------------------------------------------------------------------------
HOMEPAGE_BACKEND_INTEGRATION_SCOPE   = REQUIRED_BEFORE_FINAL_DELIVERY_NOT_RELEASE_BLOCKING (R1)
RESEARCH_WRITE_UI_SCOPE              = REQUIRED_FOR_CURRENT_DELIVERY (R1)
ADMIN_APPROVAL_UI_SCOPE              = FUTURE (R3)
MEDIA_UPLOAD_UI_SCOPE                = FUTURE (R3)
MEDIA_REVIEW_UI_SCOPE                = FUTURE (R3)

515_PAPER_FULLTEXT_SCOPE             = POST_DELIVERY_CONTENT_WORK (R2)
349_ACUPOINT_DEEP_DIGITIZATION_SCOPE = POST_DELIVERY_CONTENT_WORK (R2)

--------------------------------------------------------------------------------
ACTIONABLE BACKLOG SUMMARY
--------------------------------------------------------------------------------
R0_CURRENT_RELEASE_MANDATORY : 0 项 (底层框架与核心架构已无任何发布阻断缺陷)
R1_CURRENT_DELIVERY_REQUIRED : 3 项
   - REM-01: 研究工作台前端在线新增项目与笔记表单 UI 及 API 联通 (Owner: Pi / Claude / Codex)
   - REM-02: 首页 /api/v1/public/home 接入与既有降级行为保持 (Owner: Pi / Claude / Codex)
   - REM-03: 《用户与学者操作指南》 (Owner: DOCUMENTATION / Gemini / Claude / Codex)
R2_POST_DELIVERY_CONTENT     : 2 项 (REM-04: 349穴位全量条文录入; REM-05: 515篇论文全文深度检索)
R3_FUTURE_ENHANCEMENTS       : FROZEN_OUTSIDE_CURRENT_CLOSEOUT (REM-06: 管理员在线成果审批与媒体上传UI)
OUT_OF_SCOPE                 : 0 项

--------------------------------------------------------------------------------
DELIVERY GATES ASSESSMENT
--------------------------------------------------------------------------------
GATE_A_SOFTWARE_RELEASE : PASS (当前 RC 无发布阻断项，SOFTWARE_RELEASE_READY = YES)
GATE_B_CUSTOMER_DELIVERY: OPEN (阻断项: REM-01, REM-02, REM-03)
GATE_C_CONTENT_COMPLETION: CAN_REMAIN_OPEN_AFTER_GATE_B = YES

--------------------------------------------------------------------------------
FINAL VERDICTS
--------------------------------------------------------------------------------
SOFTWARE_RELEASE_READY  = YES (当前 RC 没有软件发布阻断项)
SOFTWARE_COMPLETE       = NO  (本期软件产品功能待完成 REM-01/02 两个交付功能)
CUSTOMER_DELIVERY_READY = NO  (所有 R1 交付项待完成)
CONTENT_COMPLETE        = NO  (交付后由文献学团队持续进行 R2 录入)

VERDICT: BASELINE_CORRECTED_AND_FROZEN
================================================================================
```
