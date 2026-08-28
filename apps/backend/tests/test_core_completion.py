"""CORE-COMPLETION dry-run semantics tests (Phase 0.4 — corrected).

Corrected per Codex substantive acceptance FAIL (e26598f): C1 emits no
synthetic absent-field candidates; C2 exercises the genuine
SourceRef.page_location → Locator rule (Edition.file_path never enters C2);
dedup identity is source-grounded. Real-data assertions read the frozen HFB
snapshot source artifact (sha256-verified).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from hfm.completion.migration import (
    MIGRATION_VERSION,
    RunResult,
    citation_target_mapping_rule,
    derive_candidate_id,
    edition_dedup_identity,
    edition_preservation_candidate,
    person_bio_assertion_candidates,
    reconciliation_manifest,
    run_dry_run,
    source_ref_page_location_to_locator,
    validate_edition_record,
)
from hfm.core.hashing import calculate_bytes_sha256

HFM_ROOT = Path(__file__).resolve().parents[3]
HFB_ROOT = Path("/Users/likeming/Sites/hfb")
SOURCE_RELPATH = "apps/frontend/src/data/huangfu_mi_exhibition.json"
EXPECTED_SOURCE_SHA256 = "94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb"
EVIDENCE_PATH = HFM_ROOT / "artifacts" / "audit" / "hfm-phase0.4-core-completion.json"

_PERSON = {
    "name": "皇甫谧",
    "name_zh": "皇甫謐",
    "birth_year": 215,
    "death_year": 282,
    "birth_place": "安定朝那",
    "dynasty": "魏晋",
}


def _source_sha() -> str:
    return "a" * 64


def _run(
    persons: list[Any] | None = None,
    editions: list[Any] | None = None,
    citations: list[Any] | None = None,
    source: dict[str, Any] | None = None,
) -> RunResult:
    src = (
        source if source is not None else {"raw": b"{}", "sha256": _source_sha(), "path": "fixture"}
    )
    return run_dry_run(src, persons or [], editions or [], citations or [])


# ---------------------------------------------------------------------------
# 1-5. C1: present-field transformation / absent biography / counts /
#       provenance / no synthetic empty assertion
# ---------------------------------------------------------------------------


def test_c1_present_field_produces_exactly_one_assertion() -> None:
    claims = person_bio_assertion_candidates(_PERSON, _source_sha())
    by_field = {c.payload["source_field"]: c for c in claims}
    assert by_field["birth_year"].payload["predicate"] == "born_in_year"
    assert by_field["birth_year"].payload["value"] == "215"
    assert by_field["death_year"].payload["predicate"] == "died_in_year"
    assert by_field["birth_place"].payload["predicate"] == "born_in"
    assert by_field["dynasty"].payload["predicate"] == "lived_in_dynasty"
    assert len(claims) == 4


def test_c1_absent_biography_creates_no_candidate() -> None:
    person = dict(_PERSON)  # no "biography" key, no "notable_works" key
    claims = person_bio_assertion_candidates(person, _source_sha())
    assert all(c.payload["source_field"] != "biography" for c in claims)
    assert all(c.payload["source_field"] != "notable_works" for c in claims)


def test_c1_count_reflects_actual_source_fields() -> None:
    claims = person_bio_assertion_candidates(_PERSON, _source_sha())
    assert len(claims) == 4  # birth_year, death_year, birth_place, dynasty


def test_c1_provenance_points_to_actual_source_field() -> None:
    claims = person_bio_assertion_candidates(_PERSON, _source_sha())
    for c in claims:
        assert c.payload["source_field"] in ("birth_year", "death_year", "birth_place", "dynasty")
        assert c.payload["source_artifact"] == "huangfu_mi_exhibition.json"
        assert c.payload["migration_rule"].startswith("PERSON_BIO")


def test_c1_no_empty_synthetic_assertion() -> None:
    claims = person_bio_assertion_candidates(_PERSON, _source_sha())
    assert all(str(c.payload["value"]).strip() != "" for c in claims)
    assert all(c.payload["source_field"] in _PERSON for c in claims)


# ---------------------------------------------------------------------------
# 6-7. C2: genuine page_location → Locator; Edition.file_path cannot enter C2
# ---------------------------------------------------------------------------


def test_c2_genuine_page_location_to_locator() -> None:
    loc = source_ref_page_location_to_locator(
        "针灸甲乙经/宋刻本/卷一/第3页", _source_sha(), "sourceref:r1"
    )
    assert loc.class_id == "C2" and loc.kind == "locator"
    assert loc.payload["locator"]["work"] == "针灸甲乙经"
    assert loc.payload["locator"]["edition"] == "宋刻本"
    assert loc.payload["locator"]["version"] == "卷一"
    assert loc.payload["locator"]["chapter"] == "第3页"
    assert loc.payload["migration_rule"].startswith("SOURCE_REF_LOCATOR")


def test_c2_zero_frozen_rows() -> None:
    """The frozen snapshot has no SourceRef.page_location rows → C2 = 0."""
    result = _run(persons=[_PERSON], editions=[])
    c2 = result.reconciliation["C2"]
    assert c2.source == 0 and c2.accepted == 0 and c2.transformed == 0 and c2.target == 0


def test_c2_edition_file_path_not_counted() -> None:
    """92 Edition.file_path records must NOT appear in any C2 counter."""
    editions = [
        {
            "id": f"e{i}",
            "work_title": "针灸甲乙经",
            "version_name": f"v{i}",
            "file_path": f"hfmzl/针灸甲乙经/论著/{i}.pdf",
        }
        for i in range(92)
    ]
    result = _run(persons=[_PERSON], editions=editions)
    c2 = result.reconciliation["C2"]
    assert c2.source == 0 and c2.transformed == 0
    assert result.source_universe == 4 + 92


# ---------------------------------------------------------------------------
# 8. C3 zero-row transformation semantics
# ---------------------------------------------------------------------------


def test_c3_zero_row_and_rule() -> None:
    result = _run(persons=[_PERSON], editions=[])
    c3 = result.reconciliation["C3"]
    assert c3.source == 0 and c3.transformed == 0
    for t in ("variant", "academic_relation", "passage"):
        assert citation_target_mapping_rule(t)["target_type"] == t
    with pytest.raises(ValueError):
        citation_target_mapping_rule("unknown")


# ---------------------------------------------------------------------------
# 9-10. Dedup: exact duplicate / same title+version distinct source identity
# ---------------------------------------------------------------------------


def test_dedup_exact_duplicate_deduplicated() -> None:
    edition = {
        "id": "e1",
        "work_title": "针灸甲乙经",
        "version_name": "10023266",
        "file_path": "d/1.pdf",
    }
    result = _run(persons=[_PERSON], editions=[edition, edition])
    assert result.edition_preserved == 1
    assert len(result.duplicates) == 1


def test_dedup_same_title_version_distinct_source_identity() -> None:
    """Same (work_title, version_name) but distinct source ids → both preserved."""
    editions = [
        {
            "id": "e1",
            "work_title": "针灸甲乙经",
            "version_name": "10023266",
            "file_path": "d/1.pdf",
        },
        {
            "id": "e2",
            "work_title": "针灸甲乙经",
            "version_name": "10023266",
            "file_path": "d/2.pdf",
        },
    ]
    result = _run(persons=[_PERSON], editions=editions)
    assert result.edition_preserved == 2
    assert result.duplicates == []
    assert edition_dedup_identity(editions[0], _source_sha()) != edition_dedup_identity(
        editions[1], _source_sha()
    )


def test_dedup_identity_source_grounded() -> None:
    a = {"id": "e1", "work_title": "针灸甲乙经", "version_name": "10023266"}
    b = {"id": "e1", "work_title": "针灸甲乙经", "version_name": "10023266"}
    c = {"id": "e2", "work_title": "针灸甲乙经", "version_name": "10023266"}
    assert edition_dedup_identity(a, _source_sha()) == edition_dedup_identity(b, _source_sha())
    assert edition_dedup_identity(a, _source_sha()) != edition_dedup_identity(c, _source_sha())
    assert edition_dedup_identity(a, "b" * 64) != edition_dedup_identity(a, _source_sha())


# ---------------------------------------------------------------------------
# 11-12. Deterministic UUID identity / candidate-set hash determinism
# ---------------------------------------------------------------------------


def test_deterministic_candidate_identity() -> None:
    sha = _source_sha()
    a1 = derive_candidate_id(sha, "C1", "person:皇甫谧|birth_year")
    a2 = derive_candidate_id(sha, "C1", "person:皇甫谧|birth_year")
    b = derive_candidate_id(sha, "C1", "person:皇甫谧|death_year")
    e1 = derive_candidate_id(sha, "EDITION_PRESERVATION", "edition:e1")
    e2 = derive_candidate_id(sha, "EDITION_PRESERVATION", "edition:e2")
    assert a1 == a2 and a1 != b and e1 != e2


def test_candidate_set_hash_deterministic() -> None:
    r1 = _run(persons=[_PERSON], editions=[])
    r2 = _run(persons=[_PERSON], editions=[])
    assert r1.candidate_set_sha256 == r2.candidate_set_sha256


# ---------------------------------------------------------------------------
# 13. Reconciliation (transformation scope + universe)
# ---------------------------------------------------------------------------


def test_reconciliation_corrected() -> None:
    result = _run(persons=[_PERSON], editions=[])
    total = result.total
    assert total.as_dict() == {
        "source": 4,
        "accepted": 4,
        "transformed": 4,
        "rejected": 0,
        "duplicate": 0,
        "target": 4,
    }
    # transformation-scope equations
    assert total.source == total.accepted + total.rejected + total.duplicate
    assert total.accepted == total.transformed
    assert total.target == total.transformed
    assert result.source_universe == 4  # no editions in this fixture


def test_reconciliation_universe_with_editions() -> None:
    editions = [
        {
            "id": f"e{i}",
            "work_title": "针灸甲乙经",
            "version_name": f"v{i}",
            "file_path": f"d/{i}.pdf",
        }
        for i in range(92)
    ]
    result = _run(persons=[_PERSON], editions=editions)
    assert result.total.target == 4
    assert result.source_universe == 96
    assert result.edition_preserved == 92
    assert len(result.preservation_candidates) == 92
    # universe equation: source_universe = transformation source + preserved editions
    assert result.source_universe == result.total.source + result.edition_preserved


def test_edition_validation_rejection() -> None:
    bad = {
        "id": "",
        "work_title": "",
        "version_name": None,
        "file_path": "",
        "size_mb": "not-a-number",
    }
    reasons = validate_edition_record(bad)
    assert {
        "missing_source_record_id",
        "missing_work_title",
        "missing_version_name",
        "missing_file_path",
        "non_numeric_size_mb",
    } <= set(reasons)


def test_edition_preservation_candidate_non_transforming() -> None:
    edition = {
        "id": "e1",
        "work_title": "针灸甲乙经",
        "version_name": "10023266",
        "dynasty": "现代",
        "edition_type": "校注本",
        "repository": "学术机构",
        "file_path": "hfmzl/针灸甲乙经/论著/10023266.pdf",
        "size_mb": 9.05,
    }
    cand = edition_preservation_candidate(edition, _source_sha())
    assert cand.class_id == "EDITION_PRESERVATION"
    assert cand.kind == "source_preservation"
    assert "non-transforming" in cand.payload["handling"]
    assert cand.payload["source_record_id"] == "e1"


# ---------------------------------------------------------------------------
# 14-15. Reproducibility / same-target idempotency
# ---------------------------------------------------------------------------


def test_reproducibility() -> None:
    src = {"raw": b"{}", "sha256": _source_sha(), "path": "fixture"}
    editions = [
        {
            "id": f"e{i}",
            "work_title": "针灸甲乙经",
            "version_name": f"v{i}",
            "file_path": f"d/{i}.pdf",
        }
        for i in range(5)
    ]
    r1 = run_dry_run(src, [_PERSON], editions, [])
    r2 = run_dry_run(src, [_PERSON], editions, [])
    assert reconciliation_manifest(r1) == reconciliation_manifest(r2)


def test_same_target_idempotency() -> None:
    """Strategy §5: applying the same frozen source twice to the SAME target
    adds 0 rows (candidate_id PRIMARY KEY, INSERT OR IGNORE)."""
    import os
    import sqlite3
    import tempfile

    result = _run(persons=[_PERSON], editions=[])
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        con = sqlite3.connect(db)
        con.execute(
            "CREATE TABLE candidates (class_id TEXT, kind TEXT, "
            "candidate_id TEXT PRIMARY KEY, payload TEXT)"
        )
        rows = [
            (c.class_id, c.kind, c.candidate_id, json.dumps(c.payload)) for c in result.candidates
        ]
        con.executemany("INSERT OR IGNORE INTO candidates VALUES (?,?,?,?)", rows)
        con.commit()
        first = con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        con.executemany("INSERT OR IGNORE INTO candidates VALUES (?,?,?,?)", rows)
        con.commit()
        second = con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        new_rows = second - first
        con.close()
        assert first == 4
        assert new_rows == 0
        assert second == first
    finally:
        os.unlink(db)


# ---------------------------------------------------------------------------
# 16-17. Failure propagation / isolation + committed evidence
# ---------------------------------------------------------------------------


def test_fail_closed() -> None:
    with pytest.raises(ValueError):
        citation_target_mapping_rule("unsupported")
    result = _run(
        persons=[_PERSON],
        editions=[],
        citations=[{"id": "c1", "target_type": "variant"}],
    )
    assert result.errors == []
    assert result.reconciliation["C3"].transformed == 1


def test_committed_evidence_artifact_corrected() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert evidence["migration_version"] == MIGRATION_VERSION
    assert evidence["failed_previous_candidate"] == "e26598f3be8b3e8b9decd902c9a5e929f0e59e2a"
    assert evidence["previous_acceptance"] == "FAIL"
    assert len(evidence["correction_reasons"]) == 3
    for run_key in ("run_a", "run_b"):
        rc = evidence[run_key]["reconciliation"]
        assert rc == {
            "source": 4,
            "accepted": 4,
            "transformed": 4,
            "rejected": 0,
            "duplicate": 0,
            "target": 4,
        }
        assert evidence[run_key]["source_universe"] == 96
        assert evidence[run_key]["edition_preserved"] == 92
    assert evidence["reproducibility"]["result"] == "PASS"
    assert evidence["idempotency"]["second_application_new_rows"] == 0
    assert evidence["isolation"]["persistent_state_after_dry_run"] == "NONE"
    assert evidence["errors"] == []
    assert evidence["silent_failure_paths"] == 0


def test_source_digest_and_evidence_consistent() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert evidence["source_sha256"] == EXPECTED_SOURCE_SHA256
    source_path = HFB_ROOT / SOURCE_RELPATH
    assert source_path.exists()
    assert calculate_bytes_sha256(source_path.read_bytes()) == EXPECTED_SOURCE_SHA256


def test_no_live_hfm_db_touched() -> None:
    assert not (HFM_ROOT / "ingestion_run.db").exists()
    dbs = [p for p in HFM_ROOT.glob("**/*.db") if "core-completion" in p.name]
    assert dbs == []
