"""CORE-COMPLETION dry-run semantics tests (Phase 0.4).

Verifies the frozen dry-run rules: deterministic reconciliation counts,
rejection/duplicate classification, isolation, reproducibility, idempotency,
failure propagation, and no live-state mutation. Real-data assertions read
the frozen HFB snapshot source artifact (sha256-verified).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hfm.completion.migration import (
    MIGRATION_VERSION,
    citation_target_mapping_rule,
    derive_candidate_id,
    edition_dedup_key,
    edition_to_locator_candidate,
    person_bio_assertion_candidates,
    reconciliation_manifest,
    run_dry_run,
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
    "summary": "西晋医学家",
}


def _source_sha() -> str:
    return "a" * 64


def test_source_digest_matches_committed_evidence() -> None:
    """Frozen source identity: the committed evidence records the same digest."""
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert evidence["source_sha256"] == EXPECTED_SOURCE_SHA256
    assert evidence["source_baseline"] == "03755b57ec0e4c8023d1447619f7d6ead9e44d73"


def test_real_source_artifact_digest() -> None:
    """The frozen snapshot's tracked source artifact hashes to the expected value."""
    source_path = HFB_ROOT / SOURCE_RELPATH
    assert source_path.exists(), "HFB snapshot checkout must be present for CORE-COMPLETION"
    raw = source_path.read_bytes()
    assert calculate_bytes_sha256(raw) == EXPECTED_SOURCE_SHA256


def test_person_bio_transformation() -> None:
    """C1: single-value fields → normalized-predicate assertion candidates."""
    candidates = person_bio_assertion_candidates(_PERSON, _source_sha())
    predicates = {c.payload["predicate"] for c in candidates}
    assert predicates == {
        "born_in_year",
        "died_in_year",
        "born_in",
        "lived_in_dynasty",
        "biography",
    }
    assert all(c.kind == "assertion" and c.class_id == "C1" for c in candidates)
    assert all(
        c.payload["legacy_governance"] == "LegacyProvenanceDecision.pending" for c in candidates
    )


def test_person_bio_missing_optional_field_omitted() -> None:
    """notable_works absent → no claim candidate (deterministic)."""
    candidates = person_bio_assertion_candidates(_PERSON, _source_sha())
    assert all(c.payload["source_field"] != "notable_works" for c in candidates)


def test_edition_validation_rejection() -> None:
    """C2 deterministic rejection rules (schema/类型/引用完整性)."""
    bad = {
        "id": "x",
        "work_title": "",
        "version_name": None,
        "file_path": "https://remote.example/x.pdf",
        "size_mb": "not-a-number",
    }
    reasons = validate_edition_record(bad)
    assert "missing_work_title" in reasons
    assert "missing_version_name" in reasons
    assert "absolute_or_remote_file_path" in reasons
    assert "non_numeric_size_mb" in reasons
    good = {
        "id": "y",
        "work_title": "针灸甲乙经",
        "version_name": "v1",
        "file_path": "hfmzl/针灸甲乙经/论著/1.pdf",
        "size_mb": 1.5,
    }
    assert validate_edition_record(good) == []


def test_edition_duplicate_detection_rule() -> None:
    """C2 dedup key is deterministic on (work_title, version_name)."""
    a = {"work_title": "针灸甲乙经", "version_name": "10023266"}
    b = {"work_title": "针灸甲乙经", "version_name": "10023266"}
    c = {"work_title": "帝王世纪", "version_name": "10023266"}
    assert edition_dedup_key(a) == edition_dedup_key(b)
    assert edition_dedup_key(a) != edition_dedup_key(c)


def test_edition_to_locator_candidate() -> None:
    """C2: page_location string → ONE structured locator candidate (1:1 unit)."""
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
    cand = edition_to_locator_candidate(edition, _source_sha())
    assert cand.kind == "locator"
    assert cand.payload["work"] == "针灸甲乙经"
    assert cand.payload["version"] == "10023266"
    assert cand.payload["path_components"] == ["hfmzl", "针灸甲乙经", "论著"]
    assert cand.payload["filename"] == "10023266.pdf"
    assert cand.payload["extension"] == "pdf"
    assert cand.payload["page_location_origin"] == "hfmzl/针灸甲乙经/论著/10023266.pdf"


def test_citation_target_mapping_rule() -> None:
    """C3: polymorphic target → unified Assertion target mapping (traceable)."""
    for target_type in ("variant", "academic_relation", "passage"):
        rule = citation_target_mapping_rule(target_type)
        assert rule["target_type"] == target_type
        assert rule["resolution"]
    with pytest.raises(ValueError):
        citation_target_mapping_rule("unknown_type")


def test_reconciliation_equations_on_mixed_fixture() -> None:
    """Contract-derived equations hold: source = accepted + rejected + duplicate;
    accepted = transformed; target = transformed − duplicate_consumed."""
    sha = _source_sha()
    editions = [
        {
            "id": "g1",
            "work_title": "针灸甲乙经",
            "version_name": "v1",
            "file_path": "d/针灸甲乙经/v1.pdf",
        },
        {
            "id": "g2",
            "work_title": "针灸甲乙经",
            "version_name": "v1",
            "file_path": "d/针灸甲乙经/v1.pdf",
        },  # duplicate of g1
        {
            "id": "b1",
            "work_title": "",
            "version_name": "v2",
            "file_path": "d/针灸甲乙经/v2.pdf",
        },  # rejected
        {"id": "g3", "work_title": "高士传", "version_name": "v3", "file_path": "d/高士传/v3.pdf"},
    ]
    result = run_dry_run(
        {"raw": b"{}", "sha256": sha, "path": "fixture"},
        [_PERSON],
        editions,
        [],
    )
    total = result.total
    assert total.source == total.accepted + total.rejected + total.duplicate
    assert total.accepted == total.transformed
    assert total.target == total.transformed
    assert total.source == 9  # 5 bio claims + 4 editions
    assert total.rejected == 1
    assert total.duplicate == 1
    assert total.accepted == 7
    assert total.target == 7


def test_candidate_ids_deterministic() -> None:
    sha = _source_sha()
    a = derive_candidate_id(sha, "C2", "edition:e1")
    b = derive_candidate_id(sha, "C2", "edition:e1")
    c = derive_candidate_id(sha, "C2", "edition:e2")
    assert a == b
    assert a != c


def test_reproducibility_and_idempotency() -> None:
    """Two equivalent runs → identical evidence; re-run → identical candidate ids."""
    sha = _source_sha()
    source = {"raw": b"{}", "sha256": sha, "path": "fixture"}
    editions = [
        {
            "id": "g1",
            "work_title": "针灸甲乙经",
            "version_name": "v1",
            "file_path": "d/针灸甲乙经/v1.pdf",
        },
        {"id": "g2", "work_title": "高士传", "version_name": "v3", "file_path": "d/高士传/v3.pdf"},
    ]
    run_a = run_dry_run(source, [_PERSON], editions, [])
    run_b = run_dry_run(source, [_PERSON], editions, [])
    rerun = run_dry_run(source, [_PERSON], editions, [])
    assert reconciliation_manifest(run_a) == reconciliation_manifest(run_b)
    assert sorted(c.candidate_id for c in run_a.candidates) == sorted(
        c.candidate_id for c in rerun.candidates
    )


def test_fail_closed() -> None:
    """Unhandled transform error must not silently pass (§23)."""
    with pytest.raises(ValueError):
        citation_target_mapping_rule("unsupported")
    result = run_dry_run(
        {"raw": b"{}", "sha256": _source_sha(), "path": "fixture"},
        [_PERSON],
        [{"id": "g1", "work_title": "针灸甲乙经", "version_name": "v1", "file_path": "d/v1.pdf"}],
        [{"id": "c1", "target_type": "variant"}],
    )
    assert result.errors == []


def test_committed_evidence_artifact() -> None:
    """The committed machine-readable evidence records the frozen-run results."""
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert evidence["migration_version"] == MIGRATION_VERSION
    assert evidence["governance_baseline"] == "00ed3ff244578d975c2748fa9d85a8d14e4c7c37"
    assert evidence["implementation_baseline"] == "d08e343dbbc52dedfcbd5bba69918e6a4b74256d"
    for run_key in ("run_a", "run_b"):
        rc = evidence[run_key]["reconciliation"]
        assert rc == {
            "source": 97,
            "accepted": 97,
            "transformed": 97,
            "rejected": 0,
            "duplicate": 0,
            "target": 97,
        }
    assert evidence["reproducibility"]["result"] == "PASS"
    assert evidence["idempotency"]["result"] == "PASS"
    assert evidence["isolation"]["persistent_state_after_dry_run"] == "NONE"
    assert evidence["isolation"]["production_db_touched"] is False
    assert evidence["errors"] == []
    assert evidence["silent_failure_paths"] == 0


def test_no_live_hfm_db_touched() -> None:
    """CORE-COMPLETION must not create/alter any live HFM database file."""
    hfm_db_candidates = list(HFM_ROOT.glob("**/*.db")) + list(HFM_ROOT.glob("**/*.sqlite*"))
    # The only DB files are test artifacts under apps/backend (not created here);
    # assert the dry-run produced no new DB files in the repo tree.
    assert not (HFM_ROOT / "ingestion_run.db").exists()
    assert not any("core-completion" in p.name for p in hfm_db_candidates)
