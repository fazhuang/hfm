"""Async database engine/session (CD-0 — DB foundation)."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hfm.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a session; commits on success, rolls back on error.

    Deployment finding (2026-08-31): the previous dependency only yielded the
    session without committing, so every HTTP write endpoint returned flushed
    IDs but rolled back on close — nothing persisted. Commit/rollback is the
    canonical single-point fix for all write endpoints.
    """
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise
