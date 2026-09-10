# B05 Rollback Test
- method: inject mid-import failure on scratch (b05_probe temp schema: CREATE+INSERT ok, then forced type error) inside BEGIN/COMMIT
- result: ROLLBACK executed; probe table absent after; scratch product tables unchanged
- PARTIAL_DATABASE_STATE=NO → ROLLBACK=PASS