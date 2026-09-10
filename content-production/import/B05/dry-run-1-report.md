# B05 Dry Run 1 — scratch baseline import

- database: hfm_b05_scratch (migrated 0014, 33 tables, mirror of hfm_prod@0014)
- package content: EMPTY_BY_DESIGN (all B04 objects NOT_IMPORTABLE: BLOCKING schema gaps)
- run1 result: manifest_rows=1(说明行) inserts=0 duplicates=0 delta_tables=0
- idempotency: PASS (transaction wrapper clean)
- note: real content INSERT path is blocked by schema gaps (stable-id/provenance/alias/title-normalization missing); no fake content imported.

## R1 rerun (identity-policy applied)

- fresh scratch hfm_b05_scratch (0014/33); RUN1 inserts=0 duplicates=0 delta=0 idempotency=PASS
- page-output-identity-policy applied: (ASSET_ID,PAGE) unique; A000542 p1 canonical=B02 alt=B01; duplicates_after_policy=0
