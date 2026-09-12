"""Minimal application settings (CD-0 — DB foundation).

HFM-native (ADAPT of the deferred HFB settings pattern): reads only
non-sensitive configuration from the environment; no pydantic-settings
dependency. Sensitive values are never exposed via /config (see system.py).

ND-1 B01 (runtime fail-closed): when HFM_ENV=prod the runtime itself refuses
the development fallbacks — a missing or local-default HFM_DATABASE_URL and a
missing or development-default HFM_TOKEN_SECRET raise at import/startup so the
application FAILS CLEARLY instead of silently using a localhost database or
the development token secret. Development/test behavior is unchanged.
"""

from __future__ import annotations

import os
from pathlib import Path

from hfm import __version__

PROJECT_NAME = "HFM"
VERSION = __version__
ENVIRONMENT = os.environ.get("HFM_ENV", "development")

#: Local development default DSN (frozen technical baseline). Tests override
#: with sqlite+aiosqlite for isolation. NEVER used when HFM_ENV=prod.
DEV_DATABASE_URL = "postgresql+asyncpg://hfb:change-me@127.0.0.1:5432/hfm"

#: Development token-signing default (hfm.phase1.auth). NEVER used when
#: HFM_ENV=prod.
DEV_TOKEN_SECRET = "hfm-phase1-dev-secret"

# Database URL. Defaults to a local PostgreSQL (frozen technical baseline);
# tests override with sqlite+aiosqlite for isolation.
DATABASE_URL = os.environ.get("HFM_DATABASE_URL", DEV_DATABASE_URL)

#: Token-signing secret consumed by hfm.phase1.auth (single source of truth so
#: the production guard cannot be bypassed by a second read path).
TOKEN_SECRET = os.environ.get("HFM_TOKEN_SECRET", DEV_TOKEN_SECRET)

#: Local media root for the pre-acceptance demo bytes endpoint (published media
#: only). Defaults to the repo-level hfmzl client-delivery directory; overridable
#: via HFM_MEDIA_ROOT. Production would use S3-compatible object storage (ADR-P2-01);
#: bytes are never stored in the relational DB.
MEDIA_ROOT = os.environ.get("HFM_MEDIA_ROOT", str(Path(__file__).resolve().parents[5] / "hfmzl"))


def _production_fail_closed() -> None:
    """Raise at import when HFM_ENV=prod without real required configuration."""
    if ENVIRONMENT != "prod":
        return
    problems: list[str] = []
    if not DATABASE_URL or DATABASE_URL == DEV_DATABASE_URL:
        problems.append(
            "HFM_DATABASE_URL must be set to a real production DSN "
            "(the local development default is forbidden in prod)"
        )
    if not TOKEN_SECRET or TOKEN_SECRET == DEV_TOKEN_SECRET:
        problems.append(
            "HFM_TOKEN_SECRET must be set to a real production secret "
            "(the development default is forbidden in prod)"
        )
    if problems:
        raise RuntimeError("HFM production environment fail-closed: " + "; ".join(problems))


_production_fail_closed()
