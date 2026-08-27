"""Tests for the Institution model (CD-0 — REUSE)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.institution import InstitutionStatus, InstitutionType
from hfm.repositories.institution import InstitutionRepository


async def test_institution_construction(session: AsyncSession) -> None:
    repo = InstitutionRepository(session)
    inst = await repo.create(name="中国中医科学院", type=InstitutionType.research)
    assert inst.id
    assert inst.type == InstitutionType.research
    assert inst.status == InstitutionStatus.draft


async def test_institution_invalid_type_rejected(session: AsyncSession) -> None:
    repo = InstitutionRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(name="非法类型机构", type="not-a-valid-type")


async def test_institution_crud(session: AsyncSession) -> None:
    repo = InstitutionRepository(session)
    inst = await repo.create(name="复旦大学", type=InstitutionType.university, location="上海")
    fetched = await repo.get_by_id(inst.id)
    assert fetched is not None
    assert fetched.location == "上海"
    updated = await repo.update(inst.id, location="上海市")
    assert updated is not None
    assert updated.location == "上海市"
    assert await repo.delete(inst.id) is True
    assert await repo.get_by_id(inst.id) is None
