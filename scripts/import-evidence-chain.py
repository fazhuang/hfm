#!/usr/bin/env python3
"""HFM P2 content import — evidence chain (assertions + evidences).

Operator-only controlled import of the frozen evidence candidates
(``content-production/normalized/evidence.csv``) into the canonical research
chain: one ``Evidence`` (anchored to a registered ``SourceRef``) + one
``Assertion`` (anchored to the subject Entity) per candidate, linked via
``assertion_evidences``. This is the P2 counterpart to publish-content.py —
idempotent, fail-closed, dry-run first, never publishes.

Dependencies (must be satisfied before running):
  - document source registration (scripts/register-document-sources.py) for
    every SOURCE_ASSET_ID referenced here — the Evidence provenance CHECK
    (source_ref_id IS NOT NULL OR source_passage_id IS NOT NULL) is enforced.

Fail-closed rules:
  - a malformed CSV row (unquoted comma shifting columns) is rejected, never
    silently imported;
  - a SUBJECT_ID with no matching Person entity is rejected;
  - a SOURCE_ASSET_ID with no registered SourceRef is rejected;
  - REVIEW_STATUS is mapped to a conservative confidence (LOW/MEDIUM/NEEDS_REVIEW
    /CONFLICT -> low|medium|low|low) and every assertion is admitted as
    ``editorial_status=draft`` — never approved, never published.

Note: Citations are deliberately NOT created here — a Citation pins a
Version/Passage location, and passages are empty until full-text extraction
(P2 item 1). They are a separate follow-on.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python import-evidence-chain.py --env-file ~/.hfm/secrets/prod.env
    # add --commit to write; default is --dry-run (report + rollback)
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "apps" / "backend"

EVIDENCE_CSV = REPO_ROOT / "content-production" / "normalized" / "evidence.csv"

#: Provenance marker (Assertion.created_by placeholder; no User FK — CA-026).
IMPORTER = "content-importer-p2"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_module(
    "validate_production_env", _SCRIPT_DIR / "validate-production-env.py"
)

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.core.hashing import calculate_canonical_metadata_sha256  # noqa: E402
from hfm.models.assertion import (  # noqa: E402
    Assertion,
    AssertionType,
    Confidence,
    EditorialStatus,
    assertion_evidences,
)
from hfm.models.chapter import Chapter  # noqa: E402,F401
from hfm.models.content_artifact import ContentArtifact  # noqa: E402,F401
from hfm.models.document import ContentDocument  # noqa: E402
from hfm.models.edition import Edition  # noqa: E402,F401
from hfm.models.entity import Entity, EntityType  # noqa: E402
from hfm.models.evidence import Evidence, EvidenceLevel  # noqa: E402
from hfm.models.passage import Passage  # noqa: E402,F401
from hfm.models.person import Person  # noqa: E402
from hfm.models.source import Source  # noqa: E402
from hfm.models.source_ref import SourceRef  # noqa: E402
from hfm.models.version import Version  # noqa: E402,F401
from hfm.models.work import Work  # noqa: E402,F401
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

#: REVIEW_STATUS -> conservative confidence (fail-closed to low).
_CONFIDENCE: dict[str, Confidence] = {
    "MEDIUM": Confidence.medium,
    "LOW": Confidence.low,
    "NEEDS_REVIEW": Confidence.low,
    "CONFLICT": Confidence.low,
}

#: Assertion type when the subject is a Person (all frozen candidates are).
_PERSON_ASSERTION_TYPE = AssertionType.BIOGRAPHICAL


def load_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Read the candidate CSV; return (rows, malformed_warnings)."""
    rows: list[dict[str, str]] = []
    warnings: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, restkey="_extra")
        for i, raw in enumerate(reader, start=2):
            extra = raw.get("_extra")
            if extra is not None:
                warnings.append(f"row {i}: extra unquoted columns {extra!r} -> rejected")
                continue
            rows.append({k: (v or "").strip() for k, v in raw.items()})
    return rows, warnings


async def _resolve_subject(session: AsyncSession, subject_id: str) -> str | None:
    """SUBJECT_ID (person stable_id) -> entities.id."""
    person = (
        await session.execute(select(Person).where(Person.stable_id == subject_id))
    ).scalar_one_or_none()
    return person.entity_id if person is not None else None


async def _resolve_source_ref(session: AsyncSession, asset_id: str) -> str | None:
    """SOURCE_ASSET_ID -> source_refs.id via documents -> sources -> source_refs."""
    doc = (
        await session.execute(
            select(ContentDocument).where(ContentDocument.source_asset_id == asset_id)
        )
    ).scalar_one_or_none()
    if doc is None or doc.stable_id is None:
        return None
    source = (
        await session.execute(
            select(Source).where(Source.source_key == f"document:{doc.stable_id}")
        )
    ).scalar_one_or_none()
    if source is None:
        return None
    ref = (
        await session.execute(
            select(SourceRef).where(SourceRef.source_id == source.id)
        )
    ).scalar_one_or_none()
    return ref.id if ref is not None else None


async def _run(
    db_url: str, evidence_level: EvidenceLevel, dry_run: bool
) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {"created": 0, "existing": 0, "rejected": 0}
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                rows, malformed = load_rows(EVIDENCE_CSV)
                for warning in malformed:
                    summary["rejected"] += 1
                    lines.append(f"REJECTED (malformed) {warning}")

                for row in rows:
                    evidence_id = row.get("EVIDENCE_ID", "")
                    subject_id = row.get("SUBJECT_ID", "")
                    claim_type = row.get("CLAIM_TYPE", "")
                    claim = row.get("CLAIM", "")
                    asset_id = row.get("SOURCE_ASSET_ID", "")
                    if not evidence_id or not subject_id or not claim:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED row: missing EVIDENCE_ID/SUBJECT_ID/CLAIM")
                        continue

                    existing = (
                        await session.execute(
                            select(Evidence).where(Evidence.stable_id == evidence_id)
                        )
                    ).scalar_one_or_none()
                    if existing is not None:
                        summary["existing"] += 1
                        lines.append(f"EXISTS evidence {evidence_id}")
                        continue

                    subject_entity_id = await _resolve_subject(session, subject_id)
                    if subject_entity_id is None:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED {evidence_id}: unknown SUBJECT_ID {subject_id}")
                        continue
                    source_ref_id = await _resolve_source_ref(session, asset_id)
                    if source_ref_id is None:
                        summary["rejected"] += 1
                        lines.append(
                            f"REJECTED {evidence_id}: no registered source_ref for "
                            f"SOURCE_ASSET_ID {asset_id}"
                        )
                        continue

                    review = row.get("REVIEW_STATUS", "").strip().upper()
                    confidence = _CONFIDENCE.get(review, Confidence.low)

                    evidence = Evidence(
                        stable_id=evidence_id,
                        description=claim,
                        evidence_level=evidence_level,
                        source_ref_id=source_ref_id,
                        content_hash=calculate_canonical_metadata_sha256(
                            {"stable_id": evidence_id, "description": claim, "asset_id": asset_id}
                        ),
                    )
                    session.add(evidence)
                    await session.flush()

                    assertion = Assertion(
                        subject_entity_id=subject_entity_id,
                        predicate=claim_type,
                        value=claim,
                        assertion_type=_PERSON_ASSERTION_TYPE,
                        editorial_status=EditorialStatus.draft,
                        confidence=confidence,
                        revision=1,
                        created_by=IMPORTER,
                    )
                    session.add(assertion)
                    await session.flush()

                    await session.execute(
                        assertion_evidences.insert().values(
                            assertion_id=assertion.id, evidence_id=evidence.id
                        )
                    )
                    summary["created"] += 1
                    lines.append(
                        f"CREATE {evidence_id}: {claim_type} (confidence={confidence.value})"
                    )

                if dry_run:
                    await session.rollback()
                    lines.append("DRY_RUN=ROLLED_BACK (no commit)")
                else:
                    await session.commit()
            except BaseException:
                await session.rollback()
                raise
    finally:
        await engine.dispose()
    return summary, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-level",
        choices=[e.value for e in EvidenceLevel],
        default=EvidenceLevel.LEVEL_4.value,
        help="academic evidence strength for all imported evidences (default LEVEL_4)",
    )
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="run every read and write then roll back (report only; default)",
    )
    parser.add_argument(
        "--commit", dest="dry_run", action="store_false", help="actually write (operator action)"
    )
    parser.add_argument(
        "--test-mode", action="store_true", help="isolated test runs only"
    )
    args = parser.parse_args(argv)

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        try:
            env = validator.merge_env(env, args.env_file)
        except validator.EnvConflictError as exc:
            print(f"ENV_FILE=FAIL ({exc})")
            return 1
    print(f"DB_TARGET={validator.describe_db_target(env)}")

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(env, environment=environment, allow_sqlite=False)
    if args.test_mode:
        errors = [e for e in errors if "HFM_ENV mismatch" not in e]
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        print("IMPORT_EVIDENCE_CHAIN=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0018")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("IMPORT_EVIDENCE_CHAIN=FAIL (database must be migrated at 0018)")
        return 1

    try:
        summary, lines = asyncio.run(
            _run(db_url, EvidenceLevel(args.evidence_level), args.dry_run)
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"IMPORT_EVIDENCE_CHAIN=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("IMPORT_EVIDENCE_CHAIN=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
