"""Minimal application settings (CD-0 — DB foundation).

HFM-native (ADAPT of the deferred HFB settings pattern): reads only
non-sensitive configuration from the environment; no pydantic-settings
dependency. Sensitive values are never exposed via /config (see system.py).
"""

from __future__ import annotations

import os

from hfm import __version__

PROJECT_NAME = "HFM"
VERSION = __version__
ENVIRONMENT = os.environ.get("HFM_ENV", "development")

# Database URL. Defaults to a local PostgreSQL (frozen technical baseline);
# tests override with sqlite+aiosqlite for isolation.
DATABASE_URL = os.environ.get(
    "HFM_DATABASE_URL", "postgresql+asyncpg://hfb:change-me@127.0.0.1:5432/hfm"
)
