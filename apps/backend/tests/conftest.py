"""Shared async test fixtures (SQLite in-memory, FK enforcement on)."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import hfm.models.assertion  # noqa: F401 — register models on Base.metadata
import hfm.models.chapter  # noqa: F401
import hfm.models.citation  # noqa: F401
import hfm.models.edition  # noqa: F401
import hfm.models.entity  # noqa: F401
import hfm.models.event  # noqa: F401
import hfm.models.event_relation  # noqa: F401
import hfm.models.evidence  # noqa: F401
import hfm.models.institution  # noqa: F401
import hfm.models.passage  # noqa: F401
import hfm.models.person  # noqa: F401
import hfm.models.source  # noqa: F401
import hfm.models.source_ref  # noqa: F401
import hfm.models.version  # noqa: F401
import hfm.models.work  # noqa: F401
from hfm.db.base import Base


@pytest_asyncio.fixture
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_fk(dbapi_connection: Any, connection_record: Any) -> None:  # noqa: ARG001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with factory() as s:
        yield s
