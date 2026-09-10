"""PWE-IT-01 tooling tests — mapping contract, guards, transaction, idempotency.

Read-only against hfm_prod; all DB writes go to a per-test migrated SQLite file
(never the canonical production database).
"""
from __future__ import annotations

import csv
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
TOOL = REPO_ROOT / "content-production/import/pwe-tooling/hfm_import_pwe.py"
BASELINE = REPO_ROOT / "content-production/import/pwe-mapping"
BACKEND = REPO_ROOT / "apps/backend"

_spec = importlib.util.spec_from_file_location("hfm_import_pwe", TOOL)
assert _spec and _spec.loader
pwe = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = pwe
_spec.loader.exec_module(pwe)


def _migrate(db_file: Path) -> str:
    env = {**os.environ, "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}"}
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=str(BACKEND), env=env, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, r.stderr[-500:]
    return f"sqlite+aiosqlite:///{db_file}"


@pytest.fixture()
def db_url(tmp_path: Path) -> str:
    return _migrate(tmp_path / "pwe.db")


def _run(url: str, *, apply: bool, allow: bool = False, env: str = "development", base: Path = BASELINE, fail: str | None = None):
    import asyncio

    return asyncio.run(
        pwe.run(
            database_url=url, baseline_dir=base, apply=apply,
            allow_hfm_prod=allow, env=env, report_path=None, fail_inject=fail,
        )
    )


# ---------------- mapping contract ----------------
def test_mapping_baseline_exact_sets():
    b = pwe.load_baseline(BASELINE)
    assert len(b.entities) == 31
    assert len(b.persons) == 17
    assert len(b.works) == 14
    assert len(b.editions_confirmed) == 87
    assert set(b.editions_deferred) == set(pwe.DEFERRED_EDITION_SET)
    assert len(b.editions_deferred) == 5


def test_exact_stable_id_sets_not_counts():
    """Exact-set cross-check against the independent normalized source CSVs."""
    b = pwe.load_baseline(BASELINE)
    norm = REPO_ROOT / "content-production/normalized"

    def ids(path: Path, col: str) -> set[str]:
        rows = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
        return {(r.get(col) or "").strip() for r in rows if (r.get(col) or "").strip()}

    src_persons = ids(norm / "persons.csv", "PERSON_ID")
    src_works = ids(norm / "works.csv", "WORK_ID")
    src_editions = ids(norm / "jiayi-editions.csv", "EDITION_ID")

    assert {p.stable_id for p in b.persons} == src_persons
    assert {w.stable_id for w in b.works} == src_works
    confirmed = {e.stable_id for e in b.editions_confirmed}
    assert confirmed == src_editions - set(pwe.DEFERRED_EDITION_SET)
    assert len(src_editions) == 92 and len(pwe.DEFERRED_EDITION_SET) == 5


def test_deferred_exclusion_and_confidence_split():
    b = pwe.load_baseline(BASELINE)
    assert all(e.work_stable_id in {w.stable_id for w in b.works} for e in b.editions_confirmed)
    assert all(
        e.work_stable_id
        in {"WORK-JIAYI", "WORK-DIWANG-SHIJI", "WORK-GAOSHIZHUAN"}
        for e in b.editions_confirmed
    )


def test_missing_work_fails_closed(tmp_path: Path):
    dst = tmp_path / "baseline"
    shutil.copytree(BASELINE, dst)
    p = dst / "03-edition-work-map.csv"
    rows = list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))
    for r in rows:
        if r["mapping_confidence"] == "HIGH":
            r["candidate_work_stable_id"] = "WORK-DOES-NOT-EXIST"
            break
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_duplicate_stable_id_fails_closed(tmp_path: Path):
    dst = tmp_path / "baseline"
    shutil.copytree(BASELINE, dst)
    p = dst / "04-person-identity-map.csv"
    rows = list(csv.DictReader(p.read_text(encoding="utf-8-sig").splitlines()))
    rows.append(dict(rows[0]))
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_mapping_baseline_id_pinned():
    b = pwe.load_baseline(BASELINE)
    assert b.mapping_baseline_id == pwe.EXPECTED_MAPPING_BASELINE_ID
    assert pwe.EXPECTED_MAPPING_BASELINE_ID != "__PINNED__"


def _copy_baseline(tmp_path: Path) -> Path:
    dst = tmp_path / "baseline"
    shutil.copytree(BASELINE, dst)
    return dst


def test_mapping_hash_tamper_refused(tmp_path: Path):
    dst = _copy_baseline(tmp_path)
    p = dst / "03-edition-work-map.csv"
    text = p.read_text(encoding="utf-8-sig")
    p.write_text(text.replace("HIGH", "HIGh", 1), encoding="utf-8-sig")
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_mapping_status_tamper_refused(tmp_path: Path):
    dst = _copy_baseline(tmp_path)
    p = dst / "04-person-identity-map.csv"
    text = p.read_text(encoding="utf-8-sig")
    p.write_text(text.replace("REVIEW_REQUIRED", "UNKNOWN", 1), encoding="utf-8-sig")
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_missing_controlled_input_refused(tmp_path: Path):
    dst = _copy_baseline(tmp_path)
    (dst / "02-work-canonical-map.csv").unlink()
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_replaced_input_refused(tmp_path: Path):
    dst = _copy_baseline(tmp_path)
    shutil.copyfile(dst / "04-person-identity-map.csv", dst / "02-work-canonical-map.csv")
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_signed_status_tamper_refused_even_with_consistent_manifest(tmp_path: Path):
    """B01: a self-consistent (re-manifested) but unsigned status must be rejected."""
    dst = _copy_baseline(tmp_path)
    p = dst / "review/PERSON-CONFIRMATION-REVIEW.csv"
    text = p.read_text(encoding="utf-8-sig")
    p.write_text(text.replace("CONFIRM_RECOMMENDED", "UNCONFIRMED", 1), encoding="utf-8-sig")
    pwe.write_manifest(dst)  # hashes now self-consistent -> only signed enforcement can reject
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_signed_review_required_status_refused(tmp_path: Path):
    dst = _copy_baseline(tmp_path)
    p = dst / "review/WORK-CONFIRMATION-REVIEW.csv"
    text = p.read_text(encoding="utf-8-sig")
    p.write_text(text.replace("CONFIRM_RECOMMENDED", "REVIEW_REQUIRED", 1), encoding="utf-8-sig")
    pwe.write_manifest(dst)
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


def test_demoted_confirmed_edition_refused(tmp_path: Path):
    dst = _copy_baseline(tmp_path)
    p = dst / "review/EDITION-CONFIRMATION-REVIEW.csv"
    text = p.read_text(encoding="utf-8-sig")
    p.write_text(text.replace("CONFIRM_RECOMMENDED", "DEFER_RECOMMENDED", 1), encoding="utf-8-sig")
    pwe.write_manifest(dst)
    with pytest.raises(pwe.BaselineContractError):
        pwe.load_baseline(dst)


# ---------------- dry-run / apply / idempotency ----------------
def test_dry_run_is_zero_write(db_url: str):
    rep = _run(db_url, apply=False)
    assert rep.result == "PASS"
    assert rep.transaction_result == "DRY_RUN_NO_WRITE"
    assert rep.entity.created == 31 and rep.person.created == 17
    assert rep.work.created == 14 and rep.edition.created == 87
    assert rep.edition.deferred == 5
    after = _run(db_url, apply=False)
    assert after.entity.created == 31  # still nothing written


def test_first_apply_creates_exact_graph(db_url: str):
    rep = _run(db_url, apply=True)
    assert rep.result == "PASS", rep.errors
    assert rep.transaction_result == "COMMITTED"
    assert (rep.entity.created, rep.person.created, rep.work.created, rep.edition.created) == (
        31, 17, 14, 87,
    )
    assert rep.edition.deferred == 5
    assert rep.document_before == rep.document_after == 0
    assert rep.document_changed == 0


def test_rerun_is_idempotent(db_url: str):
    _run(db_url, apply=True)
    rep2 = _run(db_url, apply=True)
    assert rep2.result == "PASS", rep2.errors
    assert rep2.entity.created == 0 and rep2.person.created == 0
    assert rep2.work.created == 0 and rep2.edition.created == 0
    assert rep2.entity.existing == 31 and rep2.person.existing == 17
    assert rep2.work.existing == 14 and rep2.edition.existing == 87


def test_deferred_never_written(db_url: str):
    _run(db_url, apply=True)
    import sqlite3

    db = db_url.split("///")[1]
    c = sqlite3.connect(db)
    got = {r[0] for r in c.execute("SELECT stable_id FROM editions")}
    assert len(got) == 87
    assert not (got & set(pwe.DEFERRED_EDITION_SET))
    # A000541 & A000529..532 absent
    assert not any(x in got for x in pwe.DEFERRED_EDITION_SET)


def test_edition_work_fk_resolves(db_url: str):
    _run(db_url, apply=True)
    import sqlite3

    db = db_url.split("///")[1]
    c = sqlite3.connect(db)
    orphan = c.execute(
        "SELECT count(*) FROM editions e LEFT JOIN works w ON e.work_id=w.id WHERE w.id IS NULL"
    ).fetchone()[0]
    assert orphan == 0


# ---------------- failure / rollback / collision ----------------
def test_rollback_on_injected_failure(db_url: str):
    rep = _run(db_url, apply=True, fail="after_works")
    assert rep.result == "FAIL"
    assert rep.transaction_result == "ROLLED_BACK"
    import sqlite3

    db = db_url.split("///")[1]
    c = sqlite3.connect(db)
    assert c.execute("SELECT count(*) FROM entities").fetchone()[0] == 0
    assert c.execute("SELECT count(*) FROM persons").fetchone()[0] == 0
    assert c.execute("SELECT count(*) FROM works").fetchone()[0] == 0
    assert c.execute("SELECT count(*) FROM editions").fetchone()[0] == 0


def test_identity_collision_rolls_back(db_url: str):
    import sqlite3


    db = db_url.split("///")[1]
    c = sqlite3.connect(db)
    c.execute("INSERT INTO entities (id, entity_type, name, created_at, updated_at) VALUES ('ENT-PERSON-HFM-HUANGFUMI','person','x',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)")
    c.execute("INSERT INTO persons (entity_id, stable_id, name_zh, domain_status, created_at, updated_at) VALUES ('ENT-PERSON-HFM-HUANGFUMI','PERSON-WRONG','x','pending',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)")
    c.commit()
    c.close()

    rep = _run(db_url, apply=True)
    assert rep.result == "FAIL"
    assert rep.transaction_result == "ROLLED_BACK"
    c = sqlite3.connect(db)
    assert c.execute("SELECT count(*) FROM works").fetchone()[0] == 0


# ---------------- guards ----------------
def test_document_baseline_protected(db_url: str):
    import sqlite3

    db = db_url.split("///")[1]
    c = sqlite3.connect(db)
    for i in range(3):
        c.execute(
            "INSERT INTO documents (id, stable_id, title, created_at, updated_at) "
            "VALUES (?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)",
            (f"d{i}", f"DOC-TEST-{i}", "t"),
        )
    c.commit()
    c.close()
    rep = _run(db_url, apply=True)
    assert rep.result == "PASS", rep.errors
    assert rep.document_before == 3 and rep.document_after == 3
    assert rep.document_changed == 0


def test_production_guard_refuses_without_authorization(tmp_path: Path, monkeypatch):
    # fake target named hfm_prod on sqlite; classify() forced to PRODUCTION
    db_file = tmp_path / "hfm_prod"
    url = _migrate(db_file)
    monkeypatch.setattr(pwe, "_classify", lambda u, n: "PRODUCTION")
    rep = _run(url, apply=True, allow=False, env="development")
    assert rep.result == "FAIL"
    assert rep.transaction_result == "REFUSED"
    assert any("hfm_prod" in e for e in rep.errors)


def test_production_authorization_matrix():
    ok = {"env": "prod", "target_class": "PRODUCTION", "actual_db_name": "hfm_prod", "allow": True}
    assert pwe._production_authorized(**ok) is True
    for k, v in (("env", "development"), ("allow", False), ("actual_db_name", "hfm_test")):
        bad = dict(ok)
        bad[k] = v
        assert pwe._production_authorized(**bad) is False


def test_migration_head_guard(tmp_path: Path):
    import sqlite3

    db_file = tmp_path / "old.db"
    c = sqlite3.connect(db_file)
    c.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)")
    c.execute("INSERT INTO alembic_version VALUES ('0014')")
    c.commit()
    c.close()
    rep = _run(f"sqlite+aiosqlite:///{db_file}", apply=True)
    assert rep.result == "FAIL"
    assert rep.transaction_result == "REFUSED"
