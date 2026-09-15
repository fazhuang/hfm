# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""Phase-2 P2-05 media & rights lifecycle tests.

Proves the frozen P2-05 acceptance criteria:
  - P2-05-AC-01 media without sufficient rights metadata cannot publish
    (fail-closed);
  - P2-05-AC-02 original vs public derivative separation with byte-hash
    binding;
  - P2-05-AC-03 withdrawal removes the public derivative from the public
    projection while retaining the row for audit;
  - P2-05-AC-04 redaction/watermark token is deterministic on fixture.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import AsyncGenerator
from datetime import date

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.phase2.media import (
    MediaAsset,
    MediaAssetState,
    MediaRights,
    MediaService,
    PrivacyClass,
)
from hfm.phase2.media.service import (
    compute_sha256,
    hash_matches,
    public_category,
    redaction_token,
    rights_sufficient,
    verify_asset_bytes,
)

#: 64-hex fixture hashes.
SHA_A = hashlib.sha256(b"original-bytes-a").hexdigest()
SHA_D = hashlib.sha256(b"derivative-bytes-d").hexdigest()
SHA_E = hashlib.sha256(b"other-bytes").hexdigest()


@pytest_asyncio.fixture
async def media(session: AsyncSession) -> AsyncGenerator[MediaService, None]:
    yield MediaService(session)


async def test_ac01_publish_fail_closed_without_rights(media: MediaService) -> None:
    """No rights metadata → never publishable (fail-closed)."""
    asset = await media.ingest(
        object_key="orig-1",
        mime_type="image/jpeg",
        byte_size=1024,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="展览授权", publication_permission=False
        ),
    )
    assert not rights_sufficient(asset)
    try:
        await media.publish(asset.object_key)
        raise AssertionError("publish must fail without publication permission")
    except ValueError:
        pass
    assert asset.publication_state == MediaAssetState.DRAFT


async def test_ac01_ingest_requires_rights(media: MediaService) -> None:
    """Ingestion without holder/license basis is rejected."""
    try:
        await media.ingest(
            object_key="orig-2",
            mime_type="image/png",
            byte_size=10,
            sha256=SHA_E,
            rights=MediaRights(holder="", license_basis=""),
        )
        raise AssertionError("ingest must reject empty rights metadata")
    except ValueError:
        pass


async def test_ac01_publish_with_rights_succeeds(media: MediaService) -> None:
    asset = await media.ingest(
        object_key="orig-3",
        mime_type="image/jpeg",
        byte_size=2048,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    published = await media.publish(asset.object_key)
    assert published.publication_state == MediaAssetState.PUBLISHED


async def test_ac02_derivative_bound_to_original(media: MediaService) -> None:
    original = await media.ingest(
        object_key="orig-4",
        mime_type="image/jpeg",
        byte_size=2048,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key="deriv-4",
        mime_type="image/webp",
        byte_size=512,
        sha256=SHA_D,
        redaction_rule="blur-faces",
    )
    linked = await media.find_original(derivative)
    assert linked is not None
    assert linked.object_key == original.object_key
    assert hash_matches(original, SHA_A)
    assert not hash_matches(original, SHA_D)


async def test_ac02_derivative_requires_existing_original(media: MediaService) -> None:
    try:
        await media.create_derivative(
            original_object_key="missing-orig",
            object_key="deriv-x",
            mime_type="image/webp",
            byte_size=1,
            sha256=SHA_D,
            redaction_rule="blur-faces",
        )
        raise AssertionError("derivative must require an existing original")
    except ValueError:
        pass


async def test_ac03_withdrawal_removes_from_public_projection(media: MediaService) -> None:
    asset = await media.ingest(
        object_key="orig-5",
        mime_type="image/jpeg",
        byte_size=1024,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    await media.publish(asset.object_key)
    assert any(a.object_key == asset.object_key for a in await media.public_projection())

    withdrawn = await media.withdraw(asset.object_key)
    assert withdrawn.publication_state == MediaAssetState.WITHDRAWN

    projection = await media.public_projection()
    assert not any(a.object_key == asset.object_key for a in projection)
    # Row retained for auditability (withdrawal never deletes the record).
    retained = await media.get(asset.object_key)
    assert retained is not None
    assert retained.publication_state == MediaAssetState.WITHDRAWN


async def test_ac03_withdrawn_derivative_excluded_from_projection(media: MediaService) -> None:
    original = await media.ingest(
        object_key="orig-6",
        mime_type="image/jpeg",
        byte_size=1024,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key="deriv-6",
        mime_type="image/webp",
        byte_size=256,
        sha256=SHA_D,
        redaction_rule="crop-seal",
    )
    await media.publish(derivative.object_key)
    assert any(a.object_key == derivative.object_key for a in await media.public_projection())
    await media.withdraw(derivative.object_key)
    assert not any(a.object_key == derivative.object_key for a in await media.public_projection())


async def test_ac04_redaction_token_deterministic(media: MediaService) -> None:
    """Same object identity + rule → same token; different rule → different."""
    first = redaction_token("orig-7", SHA_A, "blur-faces")
    again = redaction_token("orig-7", SHA_A, "blur-faces")
    other = redaction_token("orig-7", SHA_A, "crop-seal")
    assert first == again
    assert first != other
    assert len(first) == 64

    asset = await media.ingest(
        object_key="orig-7",
        mime_type="image/jpeg",
        byte_size=512,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=asset.object_key,
        object_key="deriv-7",
        mime_type="image/webp",
        byte_size=128,
        sha256=SHA_D,
        redaction_rule="blur-faces",
    )
    assert derivative.redaction_token == first
    assert derivative.redaction_token == redaction_token(
        asset.object_key, asset.sha256, "blur-faces"
    )


async def test_state_machine_rejects_withdrawn_republish(media: MediaService) -> None:
    asset = await media.ingest(
        object_key="orig-8",
        mime_type="image/jpeg",
        byte_size=512,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    await media.publish(asset.object_key)
    await media.withdraw(asset.object_key)
    try:
        await media.publish(asset.object_key)
        raise AssertionError("withdrawn media must not be re-published")
    except ValueError:
        pass


async def test_model_importable() -> None:
    """Media model registers on the accepted declarative base."""
    assert MediaAsset.__tablename__ == "media_assets"
    assert MediaAssetState.DRAFT == "draft"
    assert MediaAssetState.WITHDRAWN == "withdrawn"


class _FixtureStore:
    """Fixture-backed object store (ADR-P2-01 storage abstraction)."""

    def __init__(self, objects: dict[str, bytes]) -> None:
        self._objects = objects

    async def get_bytes(self, object_key: str) -> bytes:
        if object_key not in self._objects:
            raise OSError(object_key)
        return self._objects[object_key]


async def test_p104_expired_rights_rejected(media: MediaService) -> None:
    """Expired rights_expiry fails closed on publication (P1-04)."""
    asset = await media.ingest(
        object_key="orig-exp-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
            rights_expiry=date(2020, 1, 1),
        ),
    )
    assert not rights_sufficient(asset, today=date(2026, 1, 1))
    try:
        await media.publish(asset.object_key, today=date(2026, 1, 1))
        raise AssertionError("expired rights must deny publication")
    except ValueError:
        pass


async def test_p104_future_expiry_allowed(media: MediaService) -> None:
    """Future expiry allows publication when all other conditions hold."""
    asset = await media.ingest(
        object_key="orig-fut-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
            rights_expiry=date(2030, 1, 1),
        ),
    )
    assert rights_sufficient(asset, today=date(2026, 1, 1))
    published = await media.publish(asset.object_key, today=date(2026, 1, 1))
    assert published.publication_state == MediaAssetState.PUBLISHED


async def test_p104_expiry_boundary_deterministic(media: MediaService) -> None:
    """Expiry boundary is deterministic: expiry == today is allowed; the next
    day is denied."""
    asset = await media.ingest(
        object_key="orig-bnd-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
            rights_expiry=date(2026, 6, 1),
        ),
    )
    assert rights_sufficient(asset, today=date(2026, 6, 1))
    assert not rights_sufficient(asset, today=date(2026, 6, 2))
    assert rights_sufficient(asset, today=date(2026, 5, 31))


async def test_p105_actual_bytes_verified(media: MediaService) -> None:
    """Real artifact bytes are verified against the bound hash (P1-05)."""
    asset = await media.ingest(
        object_key="orig-bytes-1",
        mime_type="image/jpeg",
        byte_size=11,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    store = _FixtureStore({"orig-bytes-1": b"original-bytes-a"})
    assert await verify_asset_bytes(asset, store) is True
    assert compute_sha256(b"original-bytes-a") == SHA_A


async def test_p105_tampered_bytes_fail(media: MediaService) -> None:
    """Tampered object bytes fail the byte-hash verification."""
    asset = await media.ingest(
        object_key="orig-bytes-2",
        mime_type="image/jpeg",
        byte_size=12,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    store = _FixtureStore({"orig-bytes-2": b"tampered bytes"})
    assert await verify_asset_bytes(asset, store) is False


async def test_p105_declared_hash_mismatch_fail(media: MediaService) -> None:
    """A stored hash that does not match the actual bytes fails."""
    asset = await media.ingest(
        object_key="orig-bytes-3",
        mime_type="image/jpeg",
        byte_size=12,
        sha256=SHA_D,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    store = _FixtureStore({"orig-bytes-3": b"original-bytes-a"})
    assert await verify_asset_bytes(asset, store) is False


async def test_p106_derivative_self_reference_fail(media: MediaService) -> None:
    """A derivative cannot reference itself (P1-06)."""
    original = await media.ingest(
        object_key="orig-self-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    try:
        await media.create_derivative(
            original_object_key=original.object_key,
            object_key=original.object_key,
            mime_type="image/webp",
            byte_size=64,
            sha256=SHA_D,
            redaction_rule="blur",
        )
        raise AssertionError("self-referencing derivative must be rejected")
    except ValueError:
        pass


async def test_p106_derivative_distinct_hash_enforced(media: MediaService) -> None:
    """A derivative must differ in bytes from its original (separation)."""
    original = await media.ingest(
        object_key="orig-same-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    try:
        await media.create_derivative(
            original_object_key=original.object_key,
            object_key="deriv-same-1",
            mime_type="image/jpeg",
            byte_size=128,
            sha256=SHA_A,
            redaction_rule="none",
        )
        raise AssertionError("byte-identical derivative must be rejected")
    except ValueError:
        pass


async def test_p106_derivative_bytes_independently_verified(media: MediaService) -> None:
    """Derivative bytes are independently verified against its own hash."""
    original = await media.ingest(
        object_key="orig-ind-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key="deriv-ind-1",
        mime_type="image/webp",
        byte_size=20,
        sha256=SHA_D,
        redaction_rule="crop-seal",
    )
    store = _FixtureStore({"deriv-ind-1": b"derivative-bytes-d"})
    assert await verify_asset_bytes(derivative, store) is True
    assert derivative.sha256 != original.sha256


def test_p2_current_migration_head_0017() -> None:
    """Frontier-2 current-state migration verification (not an accepted-file
    modification): the authorized P2-05 schema migration leaves a single
    linear head 0017 with revisions 0001..0017."""
    import pathlib

    versions = pathlib.Path(__file__).resolve().parents[1] / "alembic" / "versions"
    revisions = set()
    for path in versions.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r'revision\s*=\s*["\']([^"\']+)["\']', text)
        if match:
            revisions.add(match.group(1))
    assert revisions == {f"{i:04d}" for i in range(1, 18)}
    assert "0017" in revisions


def test_public_category_person_material() -> None:
    """A person's own material (biography / words / later discourse / portrait)
    classifies as `person` instead of falling through to `other`."""
    assert public_category("皇甫谧/其传/其传.docx") == "person"
    assert public_category("皇甫谧/其言/其言.docx") == "person"
    assert public_category("皇甫谧/后论/后论.docx") == "person"
    assert public_category("皇甫谧画像.jpeg") == "person"


def test_public_category_marker_order_is_significant() -> None:
    """A person's film folder is a film, not person material — the movie marker
    is matched first."""
    assert public_category("皇甫谧/皇甫谧电影/皇甫谧一.mpg") == "movie"
    assert public_category("皇甫谧/皇甫谧电影/《针灸鼻祖皇甫谧》第1集 大器晚成.mpg") == "movie"


def test_public_category_existing_buckets_unchanged() -> None:
    """The pre-existing paper/classic/other classification is preserved."""
    assert public_category("针灸甲乙经/论文/针灸甲乙经/621-关于龈交穴.pdf") == "paper"
    assert public_category("针灸甲乙经/论著/高士传/《高士传》中华书局1985.pdf") == "classic"
    assert public_category("针灸甲乙经/论著/版本/某版本.pdf") == "classic"
    assert public_category("非遗佐证/证书/某证书.pdf") == "other"
    assert public_category("unknown.pdf") == "other"


# ------------------------------------------------- P2 redaction pipeline (0017)

P2_CERT = "非遗佐证/09职业技能等级认定资质/2、职业技能等级认定考评员名单.pdf"
P2_DERIV = "非遗佐证-脱敏/09职业技能等级认定资质/2、职业技能等级认定考评员名单.pdf"


async def _ingest_p2(media: MediaService, object_key: str = P2_CERT) -> MediaAsset:
    """Ingest a P2 asset the way ``import-media-assets.py`` does: fail-closed."""
    return await media.ingest(
        object_key=object_key,
        mime_type="application/pdf",
        byte_size=4096,
        sha256=SHA_A,
        rights=MediaRights(
            holder="皇甫谧文化（客户提供）",
            license_basis="customer_owned",
            publication_permission=False,
            privacy_class=PrivacyClass.P2,
        ),
    )


async def _redacted_derivative(
    media: MediaService, *, object_key: str = P2_DERIV, privacy_class: str = PrivacyClass.P2
) -> MediaAsset:
    original = await _ingest_p2(media)
    return await media.create_derivative(
        original_object_key=original.object_key,
        object_key=object_key,
        mime_type="application/pdf",
        byte_size=2048,
        sha256=SHA_D,
        redaction_rule="rasterize-and-mask",
    )


async def test_p2_original_cannot_carry_publication_permission(media: MediaService) -> None:
    """P2 material can never be granted direct publication at ingestion."""
    try:
        await media.ingest(
            object_key=P2_CERT,
            mime_type="application/pdf",
            byte_size=1,
            sha256=SHA_A,
            rights=MediaRights(
                holder="皇甫谧文化（客户提供）",
                license_basis="customer_owned",
                publication_permission=True,
                privacy_class=PrivacyClass.P2,
            ),
        )
        raise AssertionError("P2 material must not accept a publication permission")
    except ValueError:
        pass


async def test_p2_original_cannot_be_published(media: MediaService) -> None:
    """No route publishes a P2 original — even carrying a stray grant.

    Either the schema rejects the stray grant outright or the service refuses
    the publication; both are fail-closed, so the test accepts whichever
    fires first.
    """
    from sqlalchemy.exc import IntegrityError

    original = await _ingest_p2(media)
    original.publication_permission = True  # simulate a stray grant
    try:
        await media.publish(original.object_key)
        raise AssertionError("a P2 original must never be publishable")
    except (ValueError, IntegrityError):
        pass
    assert original.publication_state == MediaAssetState.DRAFT


async def test_p2_derivative_publishes_only_after_explicit_grant(media: MediaService) -> None:
    """The derivative inherits nothing publishable; the grant is the gate."""
    derivative = await _redacted_derivative(media)
    assert derivative.publication_permission is False
    assert derivative.derivative_publication_permission is False
    assert not rights_sufficient(derivative)
    try:
        await media.publish(derivative.object_key)
        raise AssertionError("an ungranted derivative must not publish")
    except ValueError:
        pass

    granted = await media.grant_derivative_publication(derivative.object_key)
    assert rights_sufficient(granted)
    published = await media.publish(granted.object_key)
    assert published.publication_state == MediaAssetState.PUBLISHED


async def test_derivative_inherits_privacy_class_and_original_stays_draft(
    media: MediaService,
) -> None:
    """Publishing the redacted derivative never moves the original."""
    original = await _ingest_p2(media)
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key=P2_DERIV,
        mime_type="application/pdf",
        byte_size=2048,
        sha256=SHA_D,
        redaction_rule="rasterize-and-mask",
    )
    assert derivative.privacy_class == PrivacyClass.P2
    await media.grant_derivative_publication(derivative.object_key)
    await media.publish(derivative.object_key)

    assert original.publication_state == MediaAssetState.DRAFT
    assert original.publication_permission is False
    projection = await media.public_projection()
    assert [a.object_key for a in projection] == [P2_DERIV]


async def test_grant_rejects_anything_that_is_not_a_redacted_derivative(
    media: MediaService,
) -> None:
    original = await _ingest_p2(media)
    try:
        await media.grant_derivative_publication(original.object_key)
        raise AssertionError("an original must never receive a derivative grant")
    except ValueError:
        pass

    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key=P2_DERIV,
        mime_type="application/pdf",
        byte_size=2048,
        sha256=SHA_D,
        redaction_rule="rasterize-and-mask",
    )
    derivative.redaction_token = None
    try:
        await media.grant_derivative_publication(derivative.object_key)
        raise AssertionError("a derivative without a redaction token must not be granted")
    except ValueError:
        pass


async def test_p3_is_never_publishable_by_any_route(media: MediaService) -> None:
    """P3 material (法人证照 / 不动产证明 / 考评员名单) stays out of the
    public projection even as a derivative."""
    original = await media.ingest(
        object_key="非遗佐证/08申报单位资质/2、不动产证明.pdf",
        mime_type="application/pdf",
        byte_size=4096,
        sha256=SHA_A,
        rights=MediaRights(
            holder="皇甫谧文化（客户提供）",
            license_basis="customer_owned",
            privacy_class=PrivacyClass.P3,
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key="非遗佐证-脱敏/08申报单位资质/2、不动产证明.pdf",
        mime_type="application/pdf",
        byte_size=2048,
        sha256=SHA_D,
        redaction_rule="rasterize-and-mask",
    )
    try:
        await media.grant_derivative_publication(derivative.object_key)
        raise AssertionError("P3 must not receive a publication grant")
    except ValueError:
        pass
    try:
        await media.publish(derivative.object_key)
        raise AssertionError("P3 must never publish")
    except ValueError:
        pass
    assert derivative.publication_state == MediaAssetState.DRAFT


async def test_db_check_p2_original_never_published(
    media: MediaService, session: AsyncSession
) -> None:
    """The schema — not just the service — refuses a published P2 original."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    original = await _ingest_p2(media)
    try:
        await session.execute(
            text(
                "UPDATE media_assets SET publication_state = 'published', "
                "publication_permission = 0 WHERE object_key = :k"
            ),
            {"k": original.object_key},
        )
        await session.flush()
        raise AssertionError("the DB must reject a published P2 original")
    except IntegrityError:
        pass


async def test_db_check_derivative_grant_requires_an_original(
    media: MediaService, session: AsyncSession
) -> None:
    """The schema refuses a derivative grant on a row without an original."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    original = await _ingest_p2(media)
    try:
        await session.execute(
            text(
                "UPDATE media_assets SET derivative_publication_permission = 1 "
                "WHERE object_key = :k"
            ),
            {"k": original.object_key},
        )
        await session.flush()
        raise AssertionError("the DB must reject a grant on an original")
    except IntegrityError:
        pass
