"""CORE-COMPLETION migration rules (Phase 0.4 dry-run — corrected).

Corrected per Codex CORE-COMPLETION substantive acceptance FAIL (e26598f):

  P1-1 C1  No synthetic candidates: only Person single-value fields that are
          ACTUALLY PRESENT in the frozen source record produce Assertions
          (4 applicable fields; absent `biography` yields NO candidate).
  P1-2 C2  Edition.file_path is NOT SourceRef.page_location. The frozen
          snapshot has 0 SourceRef.page_location rows → C2 real source = 0.
          The page_location → structured Locator rule is implemented and
          unit-tested with a genuine SourceRef.page_location fixture.
  P1-3     Dedup identity is source-grounded (migration version + source
          sha256 + immutable source record id), never a partial
          (work_title, version_name) tuple.

Edition records (92) are source-universe records with NO Frozen
transformation class (Strategy §7 defines none) → handled as
source-preservation (non-transforming): validated, preserved as source
evidence, never counted as C2.

Frozen source = HFM-CORE-DATA-MIGRATION-STRATEGY-v0.1.md §7 rules +
HFB snapshot 03755b5 tracked artifact huangfu_mi_exhibition.json.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from hfm.core.hashing import calculate_bytes_sha256, calculate_canonical_metadata_sha256

#: Frozen single-value Person biographical fields（Migration Strategy §7）.
#: A candidate is emitted ONLY for a field that is present and non-empty in
#: the actual source record — absent fields never fabricate a claim.
PERSON_BIO_FIELDS: tuple[str, ...] = (
    "birth_year",
    "death_year",
    "birth_place",
    "dynasty",
    "biography",
    "notable_works",
)

#: Present source field → normalized assertion predicate（predicate 归一）.
PERSON_BIO_PREDICATES: dict[str, str] = {
    "birth_year": "born_in_year",
    "death_year": "died_in_year",
    "birth_place": "born_in",
    "dynasty": "lived_in_dynasty",
    "biography": "biography",
    "notable_works": "notable_works",
}

#: Migration version — idempotency key component（Strategy §5）
MIGRATION_VERSION = "hfm-phase0.4-core-completion-v2"

CITATION_TARGET_TYPES: tuple[str, ...] = ("variant", "academic_relation", "passage")

#: Non-C source-preservation handling class for Edition records.
EDITION_PRESERVATION_CLASS = "EDITION_PRESERVATION"


@dataclass
class Candidate:
    """A target-form candidate record produced by the dry-run."""

    class_id: str
    kind: str
    candidate_id: str
    payload: dict[str, Any]

    def canonical(self) -> dict[str, Any]:
        return {
            "class": self.class_id,
            "kind": self.kind,
            "candidate_id": self.candidate_id,
            "payload": self.payload,
        }


@dataclass
class Reconciliation:
    """Contract-required counts（Migration Strategy §6）; mutable collector."""

    source: int = 0
    accepted: int = 0
    transformed: int = 0
    rejected: int = 0
    duplicate: int = 0
    target: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "source": self.source,
            "accepted": self.accepted,
            "transformed": self.transformed,
            "rejected": self.rejected,
            "duplicate": self.duplicate,
            "target": self.target,
        }


@dataclass
class RunResult:
    """One dry-run execution result (Run A / Run B / idempotency check)."""

    source: dict[str, Any]
    reconciliation: dict[str, Reconciliation] = field(default_factory=dict)
    total: Reconciliation = field(default_factory=Reconciliation)
    candidates: list[Candidate] = field(default_factory=list)
    rejections: list[dict[str, Any]] = field(default_factory=list)
    duplicates: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    source_sha256: str = ""
    candidate_set_sha256: str = ""
    source_universe: int = 0
    edition_preserved: int = 0
    preservation_manifest_sha256: str = ""
    target_db_rows: int = 0
    preservation_candidates: list[Candidate] = field(default_factory=list)


def derive_candidate_id(source_sha256: str, class_id: str, record_key: str) -> str:
    """Deterministic candidate id (uuid5) over the source-grounded identity.

    Same legitimate source candidate → same id; distinct candidates (distinct
    source record identity) → distinct id. The dry-run uses derived ids for
    reproducibility; a future authorized actual import would mint UUIDv7
    (Migration Strategy §7 ID rule).
    """
    namespace = uuid.uuid5(uuid.NAMESPACE_URL, source_sha256)
    return str(uuid.uuid5(namespace, f"{MIGRATION_VERSION}|{class_id}|{record_key}"))


def extract_source(path: str) -> dict[str, Any]:
    """Read the frozen source artifact and return (raw, sha256)."""
    try:
        raw = open(path, "rb").read()
    except OSError as exc:
        raise ValueError(f"frozen source artifact unreadable: {path}: {exc}") from exc
    return {"raw": raw, "sha256": calculate_bytes_sha256(raw), "path": path}


def _claim_value(value: Any) -> str | None:
    """Canonical claim string; None when the value is empty/absent."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True) if value else None
    text = str(value).strip()
    return text if text else None


def person_bio_assertion_candidates(person: dict[str, Any], source_sha256: str) -> list[Candidate]:
    """C1: Person single-value fields → Assertion 转写 candidates.

    Emits a candidate ONLY for fields actually present and non-empty in the
    source record — absent `biography`/`notable_works` produce no claim
    (P1-1 correction: synthetic candidates = 0).
    """
    candidates: list[Candidate] = []
    person_identity = str(person.get("name") or person.get("name_zh") or "unknown")
    for field_name in PERSON_BIO_FIELDS:
        if field_name not in person:
            continue  # absent field → no candidate
        value = _claim_value(person[field_name])
        if value is None:
            continue  # present-but-empty → no candidate
        candidates.append(
            Candidate(
                class_id="C1",
                kind="assertion",
                candidate_id=derive_candidate_id(
                    source_sha256, "C1", f"person:{person_identity}|{field_name}"
                ),
                payload={
                    "subject_entity": person_identity,
                    "predicate": PERSON_BIO_PREDICATES[field_name],
                    "value": value,
                    "source_field": field_name,  # provenance → actual source field
                    "source_artifact": "huangfu_mi_exhibition.json",
                    "migration_rule": "PERSON_BIO (Strategy §7: Person 单值字段 → Assertion)",
                    "legacy_governance": "LegacyProvenanceDecision.pending",
                },
            )
        )
    return candidates


def source_ref_page_location_to_locator(
    page_location: str, source_sha256: str, record_key: str
) -> Candidate:
    """C2 rule: genuine SourceRef.page_location → structured Locator.

    Frozen rule: `SourceRef.page_location` 字符串 → 结构化 Locator
    （work/edition/version/chapter/passage + 卷/篇/页/行）。

    The frozen snapshot has 0 SourceRef.page_location rows → this rule is
    exercised by deterministic unit tests with a minimal valid page_location
    fixture (never by Edition.file_path — P1-2 correction).
    """
    segments = [seg for seg in page_location.split("/") if seg]
    return Candidate(
        class_id="C2",
        kind="locator",
        candidate_id=derive_candidate_id(source_sha256, "C2", record_key),
        payload={
            "page_location": page_location,
            "locator": {
                "work": segments[0] if segments else None,
                "edition": segments[1] if len(segments) > 1 else None,
                "version": segments[2] if len(segments) > 2 else None,
                "chapter": segments[3] if len(segments) > 3 else None,
                "passage": segments[4] if len(segments) > 4 else None,
            },
            "raw_segments": segments,
            "migration_rule": "SOURCE_REF_LOCATOR (Strategy §7: SourceRef.page_location → Locator)",
            "source_artifact": "huangfu_mi_exhibition.json",
        },
    )


def citation_target_mapping_rule(target_type: str) -> dict[str, str]:
    """C3: Citation 多态 target → 统一 Assertion target 映射规则（可追溯映射表）."""
    mapping = {
        "variant": "resolve to TEXTUAL assertion for the variant's passage",
        "academic_relation": "resolve to RELATIONAL assertion for the relation",
        "passage": "resolve to assertion citing the passage's content",
    }
    if target_type not in mapping:
        raise ValueError(f"unsupported citation target type: {target_type}")
    return {"target_type": target_type, "resolution": mapping[target_type]}


def validate_edition_record(edition: dict[str, Any]) -> list[str]:
    """Deterministic schema/type/reference validation for Edition source records."""
    reasons: list[str] = []
    if not str(edition.get("id") or "").strip():
        reasons.append("missing_source_record_id")
    if not str(edition.get("work_title") or "").strip():
        reasons.append("missing_work_title")
    if not str(edition.get("version_name") or "").strip():
        reasons.append("missing_version_name")
    if not str(edition.get("file_path") or "").strip():
        reasons.append("missing_file_path")
    size_mb = edition.get("size_mb")
    if size_mb is not None and not isinstance(size_mb, (int, float)):
        try:
            float(str(size_mb))
        except ValueError:
            reasons.append("non_numeric_size_mb")
    return reasons


def edition_dedup_identity(edition: dict[str, Any], source_sha256: str) -> str:
    """Source-grounded dedup identity for Edition records (P1-3 correction).

    Key = migration version + source sha256 + immutable source record id.
    Distinct source records (distinct ids) are never collapsed even when they
    share work_title/version_name/publisher/year; exact duplicates (same id)
    deterministically deduplicate.
    """
    record_id = str(edition.get("id") or "")
    return f"{MIGRATION_VERSION}|{source_sha256}|edition:{record_id}"


def edition_preservation_candidate(edition: dict[str, Any], source_sha256: str) -> Candidate:
    """Edition → source-preservation candidate（NON-transforming handling）.

    Frozen Strategy §7 defines NO Edition transformation class; the 92
    classical_editions records are validated and preserved as source evidence
    (future migration input). They are NEVER counted as C2 rows and never
    become migration targets.
    """
    record_id = str(edition.get("id") or "")
    return Candidate(
        class_id=EDITION_PRESERVATION_CLASS,
        kind="source_preservation",
        candidate_id=derive_candidate_id(
            source_sha256, EDITION_PRESERVATION_CLASS, f"edition:{record_id}"
        ),
        payload={
            "source_record_id": record_id,
            "work_title": edition.get("work_title"),
            "version_name": edition.get("version_name"),
            "dynasty": edition.get("dynasty"),
            "edition_type": edition.get("edition_type"),
            "repository": edition.get("repository"),
            "file_path": edition.get("file_path"),
            "size_mb": edition.get("size_mb"),
            "handling": (
                "source-preservation candidate — non-transforming "
                "(Frozen Strategy §7 defines no Edition transformation class); "
                "validated and preserved as source evidence"
            ),
            "source_artifact": "huangfu_mi_exhibition.json",
        },
    )


def run_dry_run(
    source: dict[str, Any],
    persons: list[dict[str, Any]],
    editions: list[dict[str, Any]],
    citations: list[dict[str, Any]],
) -> RunResult:
    """Execute one deterministic dry-run (extract → validate → transform →
    reconcile). Fail-closed: any exception propagates and is recorded."""
    result = RunResult(source=source)
    result.source_sha256 = str(source["sha256"])
    source_sha = result.source_sha256

    try:
        # C1 — PERSON_BIO（actual present fields only）
        c1 = Reconciliation()
        c1_accept: list[Candidate] = []
        for person in persons:
            claims = person_bio_assertion_candidates(person, source_sha)
            c1.source += len(claims)
            c1.accepted += len(claims)
            c1_accept.extend(claims)
        c1.transformed += len(c1_accept)
        result.candidates.extend(c1_accept)
        c1.target += len(c1_accept)
        result.reconciliation["C1"] = c1

        # C2 — SOURCE_REF_LOCATOR（real frozen rows = 0; rule exercised by tests）
        c2 = Reconciliation()
        c2.target += 0
        result.reconciliation["C2"] = c2

        # C3 — CITATION_TARGET（real frozen rows = 0; rule exercised by tests）
        c3 = Reconciliation()
        for citation in citations:
            c3.source += 1
            target_type = citation.get("target_type")
            if target_type not in CITATION_TARGET_TYPES:
                c3.rejected += 1
                result.rejections.append(
                    {
                        "class": "C3",
                        "record_key": f"citation:{citation.get('id')}",
                        "reasons": [f"unsupported_target_type:{target_type}"],
                    }
                )
                continue
            c3.accepted += 1
            rule = citation_target_mapping_rule(target_type)
            result.candidates.append(
                Candidate(
                    class_id="C3",
                    kind="citation_target_mapping",
                    candidate_id=derive_candidate_id(
                        source_sha, "C3", f"citation:{citation.get('id')}"
                    ),
                    payload={"source_target": citation.get("target"), **rule},
                )
            )
        c3.transformed += sum(1 for c in result.candidates if c.class_id == "C3")
        c3.target += c3.transformed
        result.reconciliation["C3"] = c3

        # Editions — source-preservation（non-transforming; NOT C1/C2/C3）
        seen_editions: set[str] = set()
        edition_records_seen = 0
        for edition in editions:
            edition_records_seen += 1
            reasons = validate_edition_record(edition)
            if reasons:
                result.rejections.append(
                    {
                        "class": EDITION_PRESERVATION_CLASS,
                        "record_key": f"edition:{edition.get('id')}",
                        "reasons": reasons,
                    }
                )
                continue
            key = edition_dedup_identity(edition, source_sha)
            if key in seen_editions:
                result.duplicates.append(
                    {
                        "class": EDITION_PRESERVATION_CLASS,
                        "record_key": f"edition:{edition.get('id')}",
                        "dedup_identity": key,
                    }
                )
                continue
            seen_editions.add(key)
            result.edition_preserved += 1
            result.preservation_candidates.append(
                edition_preservation_candidate(edition, source_sha)
            )

        # transformation-class totals（six-field schema, Migration Strategy §6）
        total = Reconciliation()
        for rc in (c1, c2, c3):
            total.source += rc.source
            total.accepted += rc.accepted
            total.transformed += rc.transformed
            total.rejected += rc.rejected
            total.duplicate += rc.duplicate
            total.target += rc.target
        result.total = total
        # source universe = transformation source + all edition source records
        result.source_universe = total.source + edition_records_seen
    except Exception as exc:  # fail-closed (§23)
        result.errors.append(f"{type(exc).__name__}: {exc}")
        raise

    result.candidate_set_sha256 = calculate_canonical_metadata_sha256(
        [c.canonical() for c in result.candidates]
    )
    result.preservation_manifest_sha256 = calculate_canonical_metadata_sha256(
        [c.canonical() for c in result.preservation_candidates]
    )
    return result


def reconciliation_manifest(result: RunResult) -> dict[str, Any]:
    """Deterministic reconciliation report（Strategy §6 counts + universe）."""
    return {
        "migration_version": MIGRATION_VERSION,
        "source_sha256": result.source_sha256,
        "reconciliation": {cls: rc.as_dict() for cls, rc in sorted(result.reconciliation.items())},
        "total": result.total.as_dict(),
        "source_universe": result.source_universe,
        "edition_preserved": result.edition_preserved,
        "rejections": result.rejections,
        "duplicates": result.duplicates,
        "candidate_set_sha256": result.candidate_set_sha256,
        "target_candidate_count": len(result.candidates),
    }
