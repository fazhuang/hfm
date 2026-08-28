"""CORE-COMPLETION migration rules (Phase 0.4 dry-run).

Implements the frozen transformation classes from HFM-CORE-DATA-
MIGRATION-STRATEGY-v0.1.md §7 (source = frozen HFB snapshot `03755b5`
tracked data; targets = candidate records, NOT production rows):

  C1 PERSON_BIO      Person 单值字段 → Assertion 转写（birth_year/death_year/
                     birth_place/dynasty/biography/notable_works；legacy 数据以
                     LegacyProvenanceDecision 治理标记 — CA-025 语义）
  C2 VERSION_LOCATOR SourceRef.page_location 字符串 → 结构化 Locator
                     （work/edition/version/chapter/passage + 卷/篇/页/行）
  C3 CITATION_TARGET Citation 多态 target（Variant/AcademicRelation/Passage）
                     → 统一 Assertion target（可追溯映射表）

Determinism: candidate ids are derived (uuid5 of source-sha + class + key)
so Run A / Run B / idempotency re-runs produce byte-identical evidence.
Actual import (UUIDv7 per I5) is NOT part of the dry-run.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from hfm.core.hashing import calculate_bytes_sha256, calculate_canonical_metadata_sha256

#: Frozen single-value Person biographical fields（Migration Strategy §7）
PERSON_BIO_FIELDS: tuple[str, ...] = (
    "birth_year",
    "death_year",
    "birth_place",
    "dynasty",
    "biography",
    "notable_works",
)

#: Person fields present in the frozen source artifact and their normalized
#: assertion predicates (predicate 归一 — Assertion Contract §5).
PERSON_BIO_PREDICATES: dict[str, str] = {
    "birth_year": "born_in_year",
    "death_year": "died_in_year",
    "birth_place": "born_in",
    "dynasty": "lived_in_dynasty",
    "biography": "biography",
    "notable_works": "notable_works",
}

#: Source fields that may be absent without rejection (not in the frozen
#: source artifact, but required by the frozen field list when present).
PERSON_BIO_OPTIONAL: frozenset[str] = frozenset({"notable_works"})

#: Migration version — idempotency key component（Strategy §5）
MIGRATION_VERSION = "hfm-phase0.4-core-completion-v1"

CITATION_TARGET_TYPES: tuple[str, ...] = ("variant", "academic_relation", "passage")


@dataclass(frozen=True)
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
    target_db_rows: int = 0


def derive_candidate_id(source_sha256: str, class_id: str, record_key: str) -> str:
    """Deterministic candidate id (uuid5) for reproducibility.

    The dry-run uses derived ids so re-runs are byte-identical; a future
    authorized actual import would mint UUIDv7 per Migration Strategy §7.
    """
    namespace = uuid.uuid5(uuid.NAMESPACE_URL, source_sha256)
    return str(uuid.uuid5(namespace, f"{MIGRATION_VERSION}|{class_id}|{record_key}"))


def extract_source(path: str) -> dict[str, Any]:
    """Read the frozen source artifact and return (raw, sha256)."""
    raw = open(path, "rb").read()
    return {"raw": raw, "sha256": calculate_bytes_sha256(raw), "path": path}


def source_sha256_of(source: dict[str, Any]) -> str:
    return str(source["sha256"])


def person_bio_assertion_candidates(person: dict[str, Any], source_sha256: str) -> list[Candidate]:
    """C1: Person 单值字段 → Assertion 转写 candidates."""
    candidates: list[Candidate] = []
    for field_name in PERSON_BIO_FIELDS:
        raw_value = person.get(field_name)
        if raw_value is None:
            if field_name in PERSON_BIO_OPTIONAL:
                continue
            raw_value = ""
        if isinstance(raw_value, (list, dict)):
            value = json.dumps(raw_value, ensure_ascii=False, sort_keys=True)
        else:
            value = str(raw_value)
        candidate_id = derive_candidate_id(
            source_sha256, "C1", f"person:{person.get('name', 'unknown')}|{field_name}"
        )
        candidates.append(
            Candidate(
                class_id="C1",
                kind="assertion",
                candidate_id=candidate_id,
                payload={
                    "subject_entity": person.get("name", "unknown"),
                    "predicate": PERSON_BIO_PREDICATES[field_name],
                    "value": value,
                    "source_field": field_name,
                    "legacy_governance": "LegacyProvenanceDecision.pending",
                    "evidence": {"source_artifact": "huangfu_mi_exhibition.json"},
                },
            )
        )
    return candidates


def validate_edition_record(edition: dict[str, Any]) -> list[str]:
    """Deterministic rejection rules for C2 source records (Strategy §3
    validation: schema/类型/引用完整性)."""
    reasons: list[str] = []
    if not str(edition.get("work_title") or "").strip():
        reasons.append("missing_work_title")
    if not str(edition.get("version_name") or "").strip():
        reasons.append("missing_version_name")
    if not str(edition.get("file_path") or "").strip():
        reasons.append("missing_file_path")
    else:
        fp = str(edition["file_path"])
        if fp.startswith(("/", "http://", "https://", "\\\\")):
            reasons.append("absolute_or_remote_file_path")
    size_mb = edition.get("size_mb")
    if size_mb is not None and not isinstance(size_mb, (int, float)):
        try:
            float(str(size_mb))
        except ValueError:
            reasons.append("non_numeric_size_mb")
    return reasons


def edition_dedup_key(edition: dict[str, Any]) -> str:
    """Deterministic duplicate key for C2（Strategy §5 去重：按 migration
    version + source 哈希；记录级 key = work_title + version_name）."""
    return f"{edition.get('work_title')}|{edition.get('version_name')}"


def edition_to_locator_candidate(edition: dict[str, Any], source_sha256: str) -> Candidate:
    """C2: edition record → ONE structured Locator candidate.

    Frozen rule: `SourceRef.page_location` 字符串 → 结构化 Locator
    （work/edition/version/chapter/passage + 卷/篇/页/行）。The edition
    `file_path` is the page_location analog; it is split into structured
    components. Version context (work_title/version_name/…) is embedded for
    traceability — the target candidate unit is 1:1 with the source record.
    """
    record_key = f"edition:{edition.get('id')}"
    file_path = str(edition.get("file_path") or "")
    segments = [seg for seg in file_path.split("/") if seg]
    filename = segments[-1] if segments else ""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    return Candidate(
        class_id="C2",
        kind="locator",
        candidate_id=derive_candidate_id(source_sha256, "C2", record_key),
        payload={
            # structured locator (work/edition/version/chapter/passage + 卷/篇/页/行)
            "work": edition.get("work_title"),
            "version": edition.get("version_name"),
            "chapter": None,
            "passage": None,
            "page_location_origin": file_path,
            "path_components": segments[:-1],
            "filename": filename,
            "extension": ext,
            # version context for traceability
            "version_context": {
                "dynasty": edition.get("dynasty"),
                "edition_type": edition.get("edition_type"),
                "repository": edition.get("repository"),
                "size_mb": edition.get("size_mb"),
            },
        },
    )


def citation_target_mapping_rule(target_type: str) -> dict[str, str]:
    """C3: Citation 多态 target → 统一 Assertion target 映射规则（可追溯映射表）.

    Frozen Lineage §2.3: HFM Citation → Assertion（统一 target）。HFB 多态
    target 按目标类型解析为 Assertion 引用方式：
    """
    mapping = {
        "variant": "resolve to TEXTUAL assertion for the variant's passage",
        "academic_relation": "resolve to RELATIONAL assertion for the relation",
        "passage": "resolve to assertion citing the passage's content",
    }
    if target_type not in mapping:
        raise ValueError(f"unsupported citation target type: {target_type}")
    return {"target_type": target_type, "resolution": mapping[target_type]}


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
    source_sha = source["sha256"]
    seen: set[str] = set()

    try:
        # C1 — PERSON_BIO
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

        # C2 — VERSION_LOCATOR
        c2 = Reconciliation()
        c2_accept: list[Candidate] = []
        for edition in editions:
            c2.source += 1
            reasons = validate_edition_record(edition)
            if reasons:
                c2.rejected += 1
                result.rejections.append(
                    {
                        "class": "C2",
                        "record_key": f"edition:{edition.get('id')}",
                        "reasons": reasons,
                    }
                )
                continue
            key = edition_dedup_key(edition)
            if key in seen:
                c2.duplicate += 1
                result.duplicates.append(
                    {"class": "C2", "record_key": f"edition:{edition.get('id')}", "dedup_key": key}
                )
                continue
            seen.add(key)
            c2.accepted += 1
            c2_accept.append(edition_to_locator_candidate(edition, source_sha))
        c2.transformed += len(c2_accept)
        result.candidates.extend(c2_accept)
        c2.target += len(c2_accept)
        result.reconciliation["C2"] = c2

        # C3 — CITATION_TARGET
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

        # totals
        total = Reconciliation()
        for rc in result.reconciliation.values():
            total.source += rc.source
            total.accepted += rc.accepted
            total.transformed += rc.transformed
            total.rejected += rc.rejected
            total.duplicate += rc.duplicate
            total.target += rc.target
        result.total = total
    except Exception as exc:  # fail-closed (§23)
        result.errors.append(f"{type(exc).__name__}: {exc}")
        raise

    result.candidate_set_sha256 = calculate_canonical_metadata_sha256(
        [c.canonical() for c in result.candidates]
    )
    return result


def reconciliation_manifest(result: RunResult) -> dict[str, Any]:
    """Deterministic reconciliation report (Strategy §6 counts)."""
    return {
        "migration_version": MIGRATION_VERSION,
        "source_sha256": result.source_sha256,
        "reconciliation": {cls: rc.as_dict() for cls, rc in sorted(result.reconciliation.items())},
        "total": result.total.as_dict(),
        "rejections": result.rejections,
        "duplicates": result.duplicates,
        "candidate_set_sha256": result.candidate_set_sha256,
        "target_candidate_count": len(result.candidates),
    }
