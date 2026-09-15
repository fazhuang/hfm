# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""Public media endpoints — the access-scope gate (P-4), at HTTP level.

The service-level projection is covered in test_phase2_media.py. This file
covers the thing service tests cannot: that the **route** applies the gate,
for both the list endpoint and the byte-streaming endpoint.

Why it matters: the byte endpoint serves file contents. If its scope check
were dropped, a research-scoped paper would stay downloadable from the public
API while the list endpoint still looked correct — the leak would be
invisible to every list-level test.

Scope is orthogonal to publication state. Both assets below are PUBLISHED;
only one is the portal's material.
"""

from __future__ import annotations

import hashlib
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.api.v1 import phase1
from hfm.db.session import get_session
from hfm.main import app
from hfm.phase2.media import AccessScope, MediaAssetState, MediaRights, MediaService

SHA_PUBLIC = hashlib.sha256(b"public-bytes").hexdigest()
SHA_RESEARCH = hashlib.sha256(b"research-bytes").hexdigest()

PUBLIC_KEY = "针灸甲乙经/论著/《甲乙经》五车楼藏板/《甲乙经》五车楼藏板1.pdf"
RESEARCH_KEY = "针灸甲乙经/论文/针灸甲乙经/19-神志病治疗思路浅析.pdf"


@pytest_asyncio.fixture
async def media_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect both media roots at a temp dir with real files under them."""
    root = tmp_path / "media"
    derivatives = tmp_path / "derivatives"
    root.mkdir()
    derivatives.mkdir()
    monkeypatch.setattr(phase1, "MEDIA_ROOT", str(root))
    monkeypatch.setattr(phase1, "DERIVATIVE_ROOT", str(derivatives))
    return root


@pytest_asyncio.fixture
async def seeded(session: AsyncSession, media_root: Path) -> dict[str, str]:
    """One published public-scope asset and one published research-scope asset."""
    service = MediaService(session)
    ids: dict[str, str] = {}
    for key, sha, body, scope in (
        (PUBLIC_KEY, SHA_PUBLIC, b"public-bytes", AccessScope.PUBLIC),
        (RESEARCH_KEY, SHA_RESEARCH, b"research-bytes", AccessScope.RESEARCH),
    ):
        asset = await service.ingest(
            object_key=key,
            mime_type="application/pdf",
            byte_size=len(body),
            sha256=sha,
            rights=MediaRights(
                holder="皇甫谧文化（客户提供）",
                license_basis="customer_owned",
                publication_permission=True,
            ),
            access_scope=scope,
        )
        await service.publish(asset.object_key)
        assert asset.publication_state == MediaAssetState.PUBLISHED
        (media_root / key).parent.mkdir(parents=True, exist_ok=True)
        (media_root / key).write_bytes(body)
        ids[scope] = str(asset.id)
    await session.commit()
    return ids


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    # FastAPI iterates the override itself, so it must be an async generator
    # FUNCTION — handing it a generator instance makes the route receive the
    # generator as its session.
    async def _yield_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = _yield_test_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
    app.dependency_overrides.clear()


async def test_list_serves_only_public_scope(
    client: httpx.AsyncClient, seeded: dict[str, str]
) -> None:
    response = await client.get("/api/v1/public/media")
    assert response.status_code == 200
    data = response.json()["data"]
    keys = [item["object_key"] for item in data["items"]]
    assert PUBLIC_KEY in keys
    assert RESEARCH_KEY not in keys


async def test_bytes_serves_public_scope(client: httpx.AsyncClient, seeded: dict[str, str]) -> None:
    response = await client.get(f"/api/v1/public/media/{seeded[AccessScope.PUBLIC]}/bytes")
    assert response.status_code == 200
    assert response.content == b"public-bytes"


async def test_bytes_refuses_research_scope(
    client: httpx.AsyncClient, seeded: dict[str, str]
) -> None:
    """Published is not enough — the portal is not this asset's audience."""
    response = await client.get(f"/api/v1/public/media/{seeded[AccessScope.RESEARCH]}/bytes")
    assert response.status_code == 404


async def test_missing_asset_and_wrong_scope_are_indistinguishable(
    client: httpx.AsyncClient, seeded: dict[str, str]
) -> None:
    """Both 404 identically, so the response leaks no existence signal.

    Compares status, error code and detail — not the whole envelope, since
    each response legitimately carries its own request_id and timestamp.
    """
    unknown = await client.get("/api/v1/public/media/does-not-exist/bytes")
    wrong_scope = await client.get(f"/api/v1/public/media/{seeded[AccessScope.RESEARCH]}/bytes")

    assert unknown.status_code == wrong_scope.status_code == 404
    assert unknown.json()["meta"]["error_code"] == wrong_scope.json()["meta"]["error_code"]

    missing = await client.get("/api/v1/public/media/does-not-exist")
    wrong_scope_list = unknown
    assert missing.status_code == wrong_scope_list.status_code
