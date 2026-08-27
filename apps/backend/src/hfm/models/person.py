"""Person model (CD-1 — ADAPT).

ADAPT of HFB `models/person.py::Person` (CA-003) @ `03755b5`:
  - retained: name variants (pinyin/zh/courtesy_name/pseudonym), dynasty,
    research-domain fields (domain_status, anchor_path,
    research_relation_role, domain_relation_summary);
  - removed: single-value biographical truth fields (birth_year,
    death_year, birth_place, biography, notable_works, expertise) — per
    HFM-MIGRATION-STRATEGY §7 these become CD-4 Assertions with evidence
    provenance (I3/I4); replicating them as truth columns would violate
    the Frozen Assertion Contract;
  - rewritten: HFM canonical Person is a typed Entity (entity_id 1:1
    FK → entities.id, shared stable identity).
"""

from __future__ import annotations

import enum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class PersonDomainStatus(enum.StrEnum):
    """Research-domain state (HFB domain_status semantics)."""

    pending = "pending"
    verified = "verified"
    excluded = "excluded"


class Person(BaseModel):
    """A historical figure (皇甫谧, 张仲景, ...) as a typed Entity.

    Identity lives on the parent Entity row; this table holds
    person-specific research-domain fields only. Biographical values
    (birth/death/place/biography) are CD-4 Assertion inputs — deliberately
    absent here.
    """

    __tablename__ = "persons"

    entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="RESTRICT"),
        primary_key=True,
        comment="稳定标识（= entities.id，1:1）",
    )
    name_pinyin: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="姓名拼音")
    name_zh: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="中文名（繁体）"
    )
    courtesy_name: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="字")
    pseudonym: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="号")
    dynasty: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="朝代")
    domain_status: Mapped[PersonDomainStatus] = mapped_column(
        String(30),
        nullable=False,
        default=PersonDomainStatus.pending,
        comment="研究域状态: pending/verified/excluded",
    )
    anchor_path: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="锚点回溯路径 JSON 序列"
    )
    research_relation_role: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="皇甫谧研究域角色"
    )
    domain_relation_summary: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="皇甫谧研究域关系摘要"
    )
