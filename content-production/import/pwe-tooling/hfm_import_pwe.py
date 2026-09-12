#!/usr/bin/env python3
"""HFM PWE-IT-01 — PERSON / WORK / EDITION production importer tooling.

CONTENT IMPORT TOOLING (separate from product runtime; never auto-runs).

Consumes ONLY the DMIT-03-accepted PWE mapping baseline
(``content-production/import/pwe-mapping/``). No runtime title inference, no
identity guessing, no automatic review promotion.

Frozen accepted scope (DMIT-03 signature):
  * entity bootstrap: 31 rows (17 person + 14 work)
  * PERSON: 17 CONFIRMED, WORK: 14 CONFIRMED
  * EDITION: 87 CONFIRMED, 5 DEFERRED (must be skipped)

Deterministic cross-environment identity (never auto-increment, never random
UUID for stable identity):
  * entities.id            = ENT-PERSON-*  | ENT-WORK-*
  * persons.entity_id      = entities.id ; persons.stable_id = PERSON-*
  * works.id               = WORK-*       ; works.stable_id  = WORK-*
  * editions.id            = EDITION-*    ; editions.stable_id = EDITION-*
  * editions.work_id       = the preselected candidate WORK stable id

Guarantees: single transaction (all-or-nothing), idempotent rerun,
FK-ordered apply, exact-set reconciliation, DOCUMENT baseline protection,
hard production guard.

Usage:
  python hfm_import_pwe.py --database-url DSN            [--dry-run]
  python hfm_import_pwe.py --database-url DSN --apply    [--allow-hfm-prod]
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

EXPECTED_MIGRATION_HEAD = "0015"
PRODUCTION_DB = "hfm_prod"
FROZEN_DOCUMENT_COUNT = 675

EXPECTED_ENTITY_ROWS = 31
EXPECTED_PERSON_ROWS = 17
EXPECTED_WORK_ROWS = 14
EXPECTED_EDITION_CONFIRMED = 87
EXPECTED_EDITION_DEFERRED = 5

CONFIRMED_MAPPING_CONFIDENCE = "HIGH"
#: DMIT-03 frozen deferred edition set (exact).
DEFERRED_EDITION_SET = frozenset(
    {
        "EDITION-HFM-A000541",
        "EDITION-HFM-A000529",
        "EDITION-HFM-A000530",
        "EDITION-HFM-A000531",
        "EDITION-HFM-A000532",
    }
)

_BASELINE_FILES = {
    "entities": "01-entity-bootstrap.csv",
    "works": "02-work-canonical-map.csv",
    "editions": "03-edition-work-map.csv",
    "persons": "04-person-identity-map.csv",
}

#: Formal signed status vocabulary (DMIT-02/03 confirmation artifacts).
#:   recommendation == CONFIRM_RECOMMENDED -> accepted into candidate set
#:   recommendation == DEFER_RECOMMENDED   -> skipped (deferred)
#: Any other value (UNCONFIRMED/REVIEW_REQUIRED/REJECTED/UNKNOWN) => fail closed.
SIGNED_CONFIRM = "CONFIRM_RECOMMENDED"
SIGNED_DEFER = "DEFER_RECOMMENDED"
_VALID_RECOMMENDATIONS = frozenset({SIGNED_CONFIRM, SIGNED_DEFER})

_SIGNATURE_FILES = {
    "persons": "review/PERSON-CONFIRMATION-REVIEW.csv",
    "works": "review/WORK-CONFIRMATION-REVIEW.csv",
    "editions": "review/EDITION-CONFIRMATION-REVIEW.csv",
}

#: Every mapping/signature input the importer actually consumes (B02).
CONTROLLED_INPUTS: tuple[str, ...] = (
    "01-entity-bootstrap.csv",
    "02-work-canonical-map.csv",
    "03-edition-work-map.csv",
    "04-person-identity-map.csv",
    "review/PERSON-CONFIRMATION-REVIEW.csv",
    "review/WORK-CONFIRMATION-REVIEW.csv",
    "review/EDITION-CONFIRMATION-REVIEW.csv",
)
MANIFEST_FILENAME = "MAPPING-BASELINE-MANIFEST.json"
#: Pinned baseline identity (see MAPPING-BASELINE-MANIFEST.json); the importer
#: never auto-recomputes and accepts a new hash.
EXPECTED_MAPPING_BASELINE_ID = (
    "077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b"
)


class BaselineContractError(RuntimeError):
    """Mapping baseline violates the frozen DMIT-03 contract (fail closed)."""


class ProductionGuardError(RuntimeError):
    """The target is the canonical production database and is not authorized."""


def _cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


@dataclass(frozen=True)
class EntityRow:
    entity_stable_id: str
    entity_type: str
    canonical_name: str
    source_type: str
    source_stable_id: str


@dataclass(frozen=True)
class PersonRow:
    stable_id: str
    entity_stable_id: str
    canonical_name: str
    aliases: list[str]


@dataclass(frozen=True)
class WorkRow:
    stable_id: str
    entity_stable_id: str
    canonical_title: str
    work_type: str


@dataclass(frozen=True)
class EditionRow:
    stable_id: str
    work_stable_id: str
    edition_title: str


@dataclass
class SignedConfirmation:
    person: dict[str, str]
    work: dict[str, str]
    edition: dict[str, str]


@dataclass
class Baseline:
    entities: list[EntityRow]
    persons: list[PersonRow]
    works: list[WorkRow]
    editions_confirmed: list[EditionRow]
    editions_deferred: list[str]
    signed: SignedConfirmation = field(
        default_factory=lambda: SignedConfirmation({}, {}, {})
    )
    baseline_identity: str = ""
    mapping_baseline_id: str = ""
    baseline_hashes: dict[str, str] = field(default_factory=dict)


def _sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_manifest_entries(baseline_dir: Path) -> list[dict[str, object]]:
    """Deterministic per-input identity: relative_path + sha256 + size."""
    entries: list[dict[str, object]] = []
    for rel in CONTROLLED_INPUTS:
        path = baseline_dir / rel
        if not path.is_file():
            raise BaselineContractError(f"controlled input missing: {rel}")
        data = path.read_bytes()
        import hashlib

        entries.append(
            {"relative_path": rel, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        )
    return entries


def mapping_baseline_id(entries: list[dict[str, object]]) -> str:
    import hashlib

    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def write_manifest(baseline_dir: Path) -> str:
    """Explicit authoring-time manifest regeneration (never automatic)."""
    entries = compute_manifest_entries(baseline_dir)
    baseline_id = mapping_baseline_id(entries)
    doc = {
        "manifest_version": 1,
        "task": "HFM-PWE-IT-02-R1",
        "mapping_baseline_id": baseline_id,
        "inputs": entries,
    }
    (baseline_dir / MANIFEST_FILENAME).write_text(
        json.dumps(doc, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    return baseline_id


def verify_manifest(baseline_dir: Path, expected_id: str) -> str:
    """Verify the frozen baseline identity BEFORE any DB operation (fail closed)."""
    manifest_path = baseline_dir / MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise BaselineContractError(f"baseline manifest missing: {MANIFEST_FILENAME}")
    try:
        doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BaselineContractError(f"baseline manifest unreadable: {exc}") from exc
    entries = doc.get("inputs")
    if not isinstance(entries, list):
        raise BaselineContractError("baseline manifest has no inputs list")
    listed = [str(e.get("relative_path")) for e in entries]
    if sorted(listed) != sorted(CONTROLLED_INPUTS):
        raise BaselineContractError(
            f"manifest controlled-input set mismatch: {sorted(listed)} != {sorted(CONTROLLED_INPUTS)}"
        )
    computed = compute_manifest_entries(baseline_dir)
    if computed != entries:
        raise BaselineContractError("frozen mapping input content changed (sha256/size mismatch)")
    baseline_id = mapping_baseline_id(computed)
    if baseline_id != doc.get("mapping_baseline_id"):
        raise BaselineContractError("manifest mapping_baseline_id is inconsistent")
    if expected_id != "__PINNED__" and baseline_id != expected_id:
        raise BaselineContractError(
            f"mapping baseline id {baseline_id} != pinned {expected_id}"
        )
    return baseline_id


def load_signed_confirmation(baseline_dir: Path) -> SignedConfirmation:
    """Consume the formal DMIT-02/03 recommendation status as the signed sets."""
    out: dict[str, dict[str, str]] = {}
    for scope, rel in _SIGNATURE_FILES.items():
        path = baseline_dir / rel
        if not path.is_file():
            raise BaselineContractError(f"signed confirmation file missing: {rel}")
        try:
            raw = path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise BaselineContractError(f"cannot read signed confirmation {rel}: {exc}") from exc
        rows = list(csv.DictReader(raw.splitlines()))
        sig: dict[str, str] = {}
        for r in rows:
            sid = _cell(r, "stable_id")
            rec = _cell(r, "recommendation")
            if not sid:
                raise BaselineContractError(f"{rel}: row without stable_id")
            if rec not in _VALID_RECOMMENDATIONS:
                raise BaselineContractError(
                    f"{scope} {sid}: illegal/unsigned recommendation {rec!r} (fail closed)"
                )
            if sid in sig:
                raise BaselineContractError(f"{rel}: duplicate stable_id {sid}")
            sig[sid] = rec
        out[scope] = sig
    return SignedConfirmation(out["persons"], out["works"], out["editions"])


def load_baseline(baseline_dir: Path) -> Baseline:
    """Load and hard-validate the frozen DMIT-03 mapping baseline."""
    for key, name in _BASELINE_FILES.items():
        if not (baseline_dir / name).is_file():
            raise BaselineContractError(f"missing baseline file for {key}: {name}")

    # B02: verify frozen identity (manifest sha256/size + pinned baseline id)
    baseline_id = verify_manifest(baseline_dir, EXPECTED_MAPPING_BASELINE_ID)
    # B01: consume the formal signed recommendation status
    signed = load_signed_confirmation(baseline_dir)

    def rows(name: str) -> list[dict[str, str]]:
        path = baseline_dir / name
        try:
            raw = path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise BaselineContractError(f"cannot read baseline file {name}: {exc}") from exc
        return list(csv.DictReader(raw.splitlines()))

    ent_raw = rows(_BASELINE_FILES["entities"])
    per_raw = rows(_BASELINE_FILES["persons"])
    wor_raw = rows(_BASELINE_FILES["works"])
    edi_raw = rows(_BASELINE_FILES["editions"])

    # ---- entities ----
    entities = [
        EntityRow(
            entity_stable_id=_cell(r, "entity_stable_id"),
            entity_type=_cell(r, "entity_type"),
            canonical_name=_cell(r, "canonical_name"),
            source_type=_cell(r, "source_type"),
            source_stable_id=_cell(r, "source_stable_id"),
        )
        for r in ent_raw
    ]
    if len(entities) != EXPECTED_ENTITY_ROWS:
        raise BaselineContractError(
            f"entity rows {len(entities)} != frozen {EXPECTED_ENTITY_ROWS}"
        )
    if len({e.entity_stable_id for e in entities}) != len(entities):
        raise BaselineContractError("duplicate entity_stable_id in bootstrap")
    if {e.entity_type for e in entities} - {"person", "work"}:
        raise BaselineContractError("entity_type outside {person,work}")
    person_ents = [e for e in entities if e.entity_type == "person"]
    work_ents = [e for e in entities if e.entity_type == "work"]
    if len(person_ents) != EXPECTED_PERSON_ROWS or len(work_ents) != EXPECTED_WORK_ROWS:
        raise BaselineContractError(
            f"entity split {len(person_ents)}P/{len(work_ents)}W != "
            f"{EXPECTED_PERSON_ROWS}P/{EXPECTED_WORK_ROWS}W"
        )

    # ---- persons ----
    persons = []
    for r in per_raw:
        aliases = [a.strip() for a in _cell(r, "aliases").split("|") if a.strip()]
        persons.append(
            PersonRow(
                stable_id=_cell(r, "person_stable_id"),
                entity_stable_id=f"ENT-{_cell(r, 'person_stable_id')}",
                canonical_name=_cell(r, "canonical_name"),
                aliases=aliases,
            )
        )
    if len(persons) != EXPECTED_PERSON_ROWS:
        raise BaselineContractError(
            f"person rows {len(persons)} != frozen {EXPECTED_PERSON_ROWS}"
        )
    if len({p.stable_id for p in persons}) != len(persons):
        raise BaselineContractError("duplicate person stable_id")
    if not all(p.canonical_name for p in persons):
        raise BaselineContractError("person row without canonical_name")
    person_entity_ids = {e.entity_stable_id for e in person_ents}
    if {p.entity_stable_id for p in persons} != person_entity_ids:
        raise BaselineContractError("person<->person-entity bootstrap mismatch")
    unsigned_persons = [
        p.stable_id for p in persons if signed.person.get(p.stable_id) != SIGNED_CONFIRM
    ]
    if unsigned_persons:
        raise BaselineContractError(
            f"person rows not formally {SIGNED_CONFIRM}: {unsigned_persons[:5]}"
        )
    if set(signed.person) != {p.stable_id for p in persons}:
        raise BaselineContractError("signed person set != mapping person set")

    # ---- works ----
    works = []
    for r in wor_raw:
        works.append(
            WorkRow(
                stable_id=_cell(r, "work_stable_id"),
                entity_stable_id=f"ENT-{_cell(r, 'work_stable_id')}",
                canonical_title=_cell(r, "canonical_title"),
                work_type=_cell(r, "work_type"),
            )
        )
    if len(works) != EXPECTED_WORK_ROWS:
        raise BaselineContractError(
            f"work rows {len(works)} != frozen {EXPECTED_WORK_ROWS}"
        )
    if len({w.stable_id for w in works}) != len(works):
        raise BaselineContractError("duplicate work stable_id")
    if not all(w.work_type for w in works):
        raise BaselineContractError("work row without frozen work_type")
    work_entity_ids = {e.entity_stable_id for e in work_ents}
    if {w.entity_stable_id for w in works} != work_entity_ids:
        raise BaselineContractError("work<->work-entity bootstrap mismatch")
    unsigned_works = [w.stable_id for w in works if signed.work.get(w.stable_id) != SIGNED_CONFIRM]
    if unsigned_works:
        raise BaselineContractError(
            f"work rows not formally {SIGNED_CONFIRM}: {unsigned_works[:5]}"
        )
    if set(signed.work) != {w.stable_id for w in works}:
        raise BaselineContractError("signed work set != mapping work set")

    work_ids = {w.stable_id for w in works}

    # ---- editions ----
    confirmed: list[EditionRow] = []
    deferred: list[str] = []
    for r in edi_raw:
        ed_id = _cell(r, "edition_stable_id")
        confidence = _cell(r, "mapping_confidence")
        candidate = _cell(r, "candidate_work_stable_id")
        if ed_id in DEFERRED_EDITION_SET:
            if confidence == CONFIRMED_MAPPING_CONFIDENCE:
                raise BaselineContractError(
                    f"deferred edition {ed_id} carries CONFIRMED confidence"
                )
            if signed.edition.get(ed_id) != SIGNED_DEFER:
                raise BaselineContractError(
                    f"deferred edition {ed_id} lacks formal {SIGNED_DEFER} signature"
                )
            deferred.append(ed_id)
            continue
        if signed.edition.get(ed_id) != SIGNED_CONFIRM:
            raise BaselineContractError(
                f"edition {ed_id} lacks formal {SIGNED_CONFIRM} signature (fail closed)"
            )
        if confidence != CONFIRMED_MAPPING_CONFIDENCE:
            raise BaselineContractError(
                f"non-deferred edition {ed_id} is not CONFIRMED (confidence={confidence})"
            )
        if candidate not in work_ids:
            raise BaselineContractError(
                f"confirmed edition {ed_id} maps to missing WORK {candidate!r} (fail closed)"
            )
        confirmed.append(
            EditionRow(
                stable_id=ed_id,
                work_stable_id=candidate,
                edition_title=_cell(r, "edition_title"),
            )
        )
    if len(confirmed) != EXPECTED_EDITION_CONFIRMED:
        raise BaselineContractError(
            f"confirmed editions {len(confirmed)} != frozen {EXPECTED_EDITION_CONFIRMED}"
        )
    if set(deferred) != set(DEFERRED_EDITION_SET) or len(deferred) != EXPECTED_EDITION_DEFERRED:
        raise BaselineContractError(
            f"deferred set {sorted(deferred)} != frozen DMIT-03 set"
        )
    if len({e.stable_id for e in confirmed}) != len(confirmed):
        raise BaselineContractError("duplicate confirmed edition stable_id")
    if not all(e.edition_title for e in confirmed):
        raise BaselineContractError("confirmed edition without title")
    all_edition_ids = {e.stable_id for e in confirmed} | set(deferred)
    if set(signed.edition) != all_edition_ids:
        raise BaselineContractError("signed edition set != mapping edition set")

    hashes = {name: _sha256_file(baseline_dir / name) for name in _BASELINE_FILES.values()}
    return Baseline(
        entities=entities,
        persons=persons,
        works=works,
        editions_confirmed=confirmed,
        editions_deferred=sorted(deferred),
        signed=signed,
        baseline_identity=baseline_id,
        mapping_baseline_id=baseline_id,
        baseline_hashes=hashes,
    )


def hashlib_join(hashes: dict[str, str]) -> str:
    import hashlib

    joined = "|".join(f"{k}:{v}" for k, v in sorted(hashes.items()))
    return hashlib.sha256(joined.encode()).hexdigest()


@dataclass
class Counters:
    expected: int = 0
    created: int = 0
    existing: int = 0
    skipped: int = 0
    deferred: int = 0
    conflict: int = 0
    failed: int = 0


@dataclass
class ImportReport:
    run_id: str = ""
    timestamp: str = ""
    mode: str = "dry-run"
    database_identity: str = ""
    database_target_class: str = ""
    migration_current: str = ""
    baseline_identity: str = ""
    baseline_hashes: dict[str, str] = field(default_factory=dict)
    entity: Counters = field(default_factory=Counters)
    person: Counters = field(default_factory=Counters)
    work: Counters = field(default_factory=Counters)
    edition: Counters = field(default_factory=Counters)
    document_before: int = -1
    document_after: int = -1
    document_changed: int = -1
    transaction_result: str = "NOT_RUN"
    result: str = "NOT_RUN"
    failed: int = 0
    errors: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"RUN_ID={self.run_id}",
            f"MODE={self.mode}",
            f"DATABASE_IDENTITY={self.database_identity}",
            f"DATABASE_TARGET_CLASS={self.database_target_class}",
            f"MIGRATION_CURRENT={self.migration_current}",
            f"BASELINE_IDENTITY={self.baseline_identity}",
        ]
        for name in ("entity", "person", "work", "edition"):
            c: Counters = getattr(self, name)
            lines.append(
                f"{name.upper()}_EXPECTED={c.expected} {name.upper()}_CREATED={c.created} "
                f"{name.upper()}_EXISTING={c.existing} {name.upper()}_SKIPPED={c.skipped} "
                f"{name.upper()}_DEFERRED={c.deferred} {name.upper()}_CONFLICT={c.conflict}"
            )
        lines += [
            f"DOCUMENT_BEFORE={self.document_before}",
            f"DOCUMENT_AFTER={self.document_after}",
            f"DOCUMENT_CHANGED={self.document_changed}",
            f"TRANSACTION_RESULT={self.transaction_result}",
            f"RESULT={self.result}",
            f"FAILED={self.failed}",
        ]
        for err in self.errors:
            lines.append(f"ERROR={err}")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        body = self.render().replace("\n", "\n").strip()
        return f"# PWE Import Report\n\n```text\n{body}\n```\n"


async def _current_migration_head(conn) -> list[str] | None:
    try:
        rows = (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalars().all()
        return sorted({str(r) for r in rows})
    except Exception:  # noqa: BLE001
        return None


async def _document_count(conn) -> int:
    try:
        return int((await conn.execute(text("SELECT count(*) FROM documents"))).scalar_one())
    except Exception:  # noqa: BLE001
        return -1


async def _existing_entity_ids(session) -> set[str]:
    from hfm.models.entity import Entity

    return set((await session.execute(select(Entity.id))).scalars().all())


async def _existing_person_keys(session) -> dict[str, str | None]:
    from hfm.models.person import Person

    rows = (await session.execute(select(Person.entity_id, Person.stable_id))).all()
    return {r[0]: r[1] for r in rows}


async def _existing_work_keys(session) -> dict[str, str | None]:
    from hfm.models.work import Work

    rows = (await session.execute(select(Work.id, Work.stable_id))).all()
    return {r[0]: r[1] for r in rows}


async def _existing_edition_keys(session) -> dict[str, str | None]:
    from hfm.models.edition import Edition

    rows = (await session.execute(select(Edition.id, Edition.stable_id))).all()
    return {r[0]: r[1] for r in rows}


def _classify(url, actual_db_name: str) -> str:
    backend = url.get_backend_name()
    if backend == "postgresql":
        return "PRODUCTION" if actual_db_name == PRODUCTION_DB else "DISPOSABLE_POSTGRESQL"
    if backend == "sqlite":
        return "SQLITE"
    return "UNKNOWN"


def _production_authorized(*, env: str, target_class: str, actual_db_name: str, allow: bool) -> bool:
    return (
        env == "prod"
        and target_class == "PRODUCTION"
        and actual_db_name == PRODUCTION_DB
        and allow
    )


async def _apply_entities(session, baseline: Baseline, rep: ImportReport) -> None:
    from hfm.models.entity import Entity

    rep.entity.expected = len(baseline.entities)
    existing = await _existing_entity_ids(session)
    for e in baseline.entities:
        if e.entity_stable_id in existing:
            rep.entity.existing += 1
            continue
        session.add(
            Entity(
                id=e.entity_stable_id,
                entity_type=e.entity_type,
                name=e.canonical_name,
                name_zh=e.canonical_name,
            )
        )
        existing.add(e.entity_stable_id)
        rep.entity.created += 1


async def _apply_persons(session, baseline: Baseline, rep: ImportReport) -> None:
    from hfm.models.person import Person, PersonAlias

    rep.person.expected = len(baseline.persons)
    keys = await _existing_person_keys(session)
    existing_alias = set(
        (await session.execute(select(PersonAlias.person_id, PersonAlias.alias))).all()
    )
    for p in baseline.persons:
        if p.entity_stable_id in keys:
            if keys[p.entity_stable_id] != p.stable_id:
                raise BaselineContractError(
                    f"identity collision for {p.entity_stable_id}: "
                    f"existing stable_id {keys[p.entity_stable_id]!r} != {p.stable_id!r}"
                )
            rep.person.existing += 1
        else:
            session.add(
                Person(
                    entity_id=p.entity_stable_id,
                    id=p.stable_id,
                    stable_id=p.stable_id,
                    name_zh=p.canonical_name,
                )
            )
            keys[p.entity_stable_id] = p.stable_id
            rep.person.created += 1
        for alias in p.aliases:
            key = (p.entity_stable_id, alias)
            if key in existing_alias:
                rep.person.skipped += 1
                continue
            session.add(
                PersonAlias(person_id=p.entity_stable_id, alias=alias, alias_type="alias")
            )
            existing_alias.add(key)


async def _apply_works(session, baseline: Baseline, rep: ImportReport) -> None:
    from hfm.models.work import Work

    rep.work.expected = len(baseline.works)
    keys = await _existing_work_keys(session)
    for w in baseline.works:
        if w.stable_id in keys:
            if keys[w.stable_id] != w.stable_id:
                raise BaselineContractError(f"work identity collision {w.stable_id}")
            rep.work.existing += 1
            continue
        entity = Work(
            stable_id=w.stable_id,
            title=w.canonical_title,
            entity_id=w.entity_stable_id,
            category=w.work_type,
            author_entity_id=None,
        )
        entity.id = w.stable_id  # deterministic identity, set after entity_id (I4 guard)
        session.add(entity)
        keys[w.stable_id] = w.stable_id
        rep.work.created += 1


async def _apply_editions(session, baseline: Baseline, rep: ImportReport) -> None:
    from hfm.models.edition import Edition

    rep.edition.expected = len(baseline.editions_confirmed)
    rep.edition.deferred = len(baseline.editions_deferred)
    keys = await _existing_edition_keys(session)
    for ed in baseline.editions_confirmed:
        if ed.stable_id in keys:
            if keys[ed.stable_id] != ed.stable_id:
                raise BaselineContractError(f"edition identity collision {ed.stable_id}")
            rep.edition.existing += 1
            continue
        session.add(
            Edition(
                id=ed.stable_id,
                stable_id=ed.stable_id,
                work_id=ed.work_stable_id,
                edition_name=ed.edition_title,
            )
        )
        keys[ed.stable_id] = ed.stable_id
        rep.edition.created += 1


async def _assert_exact_sets(session, baseline: Baseline) -> None:
    """Fail-closed exact-set reconciliation after apply."""
    expected_entities = {e.entity_stable_id for e in baseline.entities}
    expected_persons = {p.stable_id for p in baseline.persons}
    expected_works = {w.stable_id for w in baseline.works}
    expected_editions = {e.stable_id for e in baseline.editions_confirmed}

    from hfm.models.edition import Edition
    from hfm.models.entity import Entity
    from hfm.models.person import Person
    from hfm.models.work import Work

    got_entities = set((await session.execute(select(Entity.id))).scalars().all())
    got_persons = set((await session.execute(select(Person.stable_id))).scalars().all())
    got_works = set((await session.execute(select(Work.stable_id))).scalars().all())
    got_editions = set((await session.execute(select(Edition.stable_id))).scalars().all())

    problems = []
    if not expected_entities <= got_entities:
        problems.append(f"entity missing {sorted(expected_entities - got_entities)[:5]}")
    if not expected_persons <= got_persons:
        problems.append(f"person missing {sorted(expected_persons - got_persons)[:5]}")
    if not expected_works <= got_works:
        problems.append(f"work missing {sorted(expected_works - got_works)[:5]}")
    if not expected_editions <= got_editions:
        problems.append(f"edition missing {sorted(expected_editions - got_editions)[:5]}")
    if set(baseline.editions_deferred) & got_editions:
        problems.append("deferred edition present after apply")
    if problems:
        raise BaselineContractError("exact-set assertion failed: " + "; ".join(problems))


async def _edition_work_fk_check(session) -> None:
    """Every imported edition.work_id must resolve to an existing works.id."""
    from hfm.models.edition import Edition
    from hfm.models.work import Work

    orphans = (
        await session.execute(
            select(Edition.id).outerjoin(Work, Edition.work_id == Work.id).where(Work.id.is_(None))
        )
    ).scalars().all()
    if orphans:
        raise BaselineContractError(f"dangling edition.work_id for {sorted(orphans)[:5]}")


async def run(
    *,
    database_url: str,
    baseline_dir: Path,
    apply: bool,
    allow_hfm_prod: bool,
    env: str,
    report_path: Path | None,
    fail_inject: str | None = None,
) -> ImportReport:
    rep = ImportReport(
        run_id=f"pwe-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(UTC).isoformat(),
        mode="apply" if apply else "dry-run",
    )
    url = make_url(database_url)

    baseline = load_baseline(baseline_dir)
    rep.baseline_identity = baseline.baseline_identity
    rep.baseline_hashes = baseline.baseline_hashes

    engine: AsyncEngine = create_async_engine(database_url, future=True)
    try:
        async with engine.connect() as conn:
            actual_db = (
                str((await conn.execute(text("SELECT current_database()"))).scalar_one())
                if url.get_backend_name() == "postgresql"
                else (Path(url.database).name if url.database else ":memory:")
            )
            rep.database_identity = actual_db
            rep.database_target_class = _classify(url, actual_db)
            heads = await _current_migration_head(conn)
            rep.migration_current = ",".join(heads) if heads is not None else "<missing>"
            rep.document_before = await _document_count(conn)
            if heads != [EXPECTED_MIGRATION_HEAD]:
                raise BaselineContractError(
                    f"migration head {rep.migration_current!r} != {EXPECTED_MIGRATION_HEAD!r}"
                )
            if rep.database_target_class == "PRODUCTION" and not _production_authorized(
                env=env,
                target_class=rep.database_target_class,
                actual_db_name=actual_db,
                allow=allow_hfm_prod,
            ):
                raise ProductionGuardError(
                    "target is hfm_prod; --allow-hfm-prod + HFM_ENV=prod required"
                )

        factory = async_sessionmaker(engine, expire_on_commit=False)

        if not apply:
            # dry-run: full validation + predicted changes, zero writes.
            async with factory() as session:
                ents = await _existing_entity_ids(session)
                per = await _existing_person_keys(session)
                wor = await _existing_work_keys(session)
                edi = await _existing_edition_keys(session)
            rep.entity.expected = len(baseline.entities)
            rep.entity.created = sum(1 for e in baseline.entities if e.entity_stable_id not in ents)
            rep.entity.existing = rep.entity.expected - rep.entity.created
            rep.person.expected = len(baseline.persons)
            rep.person.created = sum(1 for p in baseline.persons if p.entity_stable_id not in per)
            rep.person.existing = rep.person.expected - rep.person.created
            rep.work.expected = len(baseline.works)
            rep.work.created = sum(1 for w in baseline.works if w.stable_id not in wor)
            rep.work.existing = rep.work.expected - rep.work.created
            rep.edition.expected = len(baseline.editions_confirmed)
            rep.edition.created = sum(
                1 for e in baseline.editions_confirmed if e.stable_id not in edi
            )
            rep.edition.existing = rep.edition.expected - rep.edition.created
            rep.edition.deferred = len(baseline.editions_deferred)
            rep.document_after = rep.document_before
            rep.document_changed = 0
            rep.transaction_result = "DRY_RUN_NO_WRITE"
            rep.result = "PASS"
        else:
            async with factory() as session:
                try:
                    async with session.begin():
                        await _apply_entities(session, baseline, rep)
                        if fail_inject == "after_entities":
                            raise RuntimeError("injected failure after entities")
                        await _apply_persons(session, baseline, rep)
                        await _apply_works(session, baseline, rep)
                        if fail_inject == "after_works":
                            raise RuntimeError("injected failure after works")
                        await _apply_editions(session, baseline, rep)
                        await session.flush()
                        await _edition_work_fk_check(session)
                        await _assert_exact_sets(session, baseline)
                        after = await _document_count(session)
                        rep.document_after = after
                        rep.document_changed = after - rep.document_before
                        if rep.document_before >= 0 and after != rep.document_before:
                            raise BaselineContractError(
                                f"DOCUMENT baseline changed {rep.document_before}->{after}"
                            )
                    rep.transaction_result = "COMMITTED"
                    rep.result = "PASS"
                except Exception as exc:  # noqa: BLE001
                    rep.transaction_result = "ROLLED_BACK"
                    rep.result = "FAIL"
                    rep.failed = 1
                    rep.errors.append(f"{type(exc).__name__}: {exc}")
    except (BaselineContractError, ProductionGuardError) as exc:
        rep.transaction_result = "REFUSED"
        rep.result = "FAIL"
        rep.errors.append(f"{type(exc).__name__}: {exc}")
    except Exception as exc:  # noqa: BLE001
        rep.transaction_result = "ERROR"
        rep.result = "FAIL"
        rep.errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        await engine.dispose()

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rep.to_markdown(), encoding="utf-8")
        report_path.with_suffix(".json").write_text(
            json.dumps(rep.__dict__, default=str, indent=2), encoding="utf-8"
        )
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--database-url", required=True)
    ap.add_argument("--baseline-dir", type=Path, default=None)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="explicit dry-run (default)")
    ap.add_argument("--allow-hfm-prod", action="store_true")
    ap.add_argument("--report", type=Path, default=None)
    ap.add_argument(
        "--write-manifest",
        action="store_true",
        help="authoring-only: regenerate MAPPING-BASELINE-MANIFEST.json (no DB access)",
    )
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    baseline_dir = args.baseline_dir or (repo_root / "content-production/import/pwe-mapping")

    if args.write_manifest:
        new_id = write_manifest(baseline_dir)
        print(f"MAPPING_BASELINE_ID={new_id}")
        return 0

    env = os.environ.get("HFM_ENV", "development")

    rep = asyncio.run(
        run(
            database_url=args.database_url,
            baseline_dir=baseline_dir,
            apply=bool(args.apply) and not args.dry_run,
            allow_hfm_prod=args.allow_hfm_prod,
            env=env,
            report_path=args.report,
        )
    )
    print(rep.render())
    return 0 if rep.result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
