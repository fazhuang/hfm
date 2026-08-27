"""Generic async repository base (CD-0 — ADAPT).

ADAPT of HFB `apps/backend/app/repositories/base.py` @ `03755b5`:
  - retained: create / get_by_id / update / delete / count primitives;
  - removed: soft-delete (`is_deleted`), paginated search across arbitrary
    fields (not required by CD-0 canonical scope; pagination contract is
    handled by `hfm.schemas.common` at the API layer in later batches);
  - rewritten: HFM namespace, no dependency on a soft-delete Base.
"""

from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.db.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository[ModelT: BaseModel]:
    """Generic async CRUD repository bound to a model."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, id: str) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ModelT]:
        stmt = select(self.model).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        value = result.scalar_one()
        return value if value is not None else 0

    async def update(self, id: str, **kwargs: Any) -> ModelT | None:
        instance = await self.get_by_id(id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if key in self.model.immutable_fields:
                raise ValueError(
                    f"Field '{key}' is immutable on {self.model.__name__} and cannot be updated"
                )
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, id: str) -> bool:
        instance = await self.get_by_id(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True
