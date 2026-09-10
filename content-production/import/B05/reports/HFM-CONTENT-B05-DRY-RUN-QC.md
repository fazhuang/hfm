# HFM CONTENT-B05 — DRY RUN QC

- Scratch DB hfm_b05_scratch: schema 与 hfm_prod@0014 一致（33/33 表比对）
- RUN1=PASS（0 insert/0 dup/0 delta）RUN2=PASS（幂等，0 dup/0 update）
- ROLLBACK=PASS（故障注入后无 PARTIAL 状态）
- PRODUCTION_GUARD=REFUSE on hfm_prod（实测 exit 2）
- UNEXPLAINED_DELTA=0（expected 0 vs actual 0）
- 诚实边界：因 BLOCKING schema gaps，内容 INSERT 集为空；本 QC 验证的是守卫/事务/幂等/回滚机制，
  不宣称“内容已可导入”。正式导入须先完成 schema 决策。
