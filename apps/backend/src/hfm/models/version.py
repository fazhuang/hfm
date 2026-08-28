"""Version model (CD-2 — REUSE, CA-012 + I2).

REUSE of HFB `models/version.py::Version` @ `03755b5` (version_name, era,
year, repository, shelf_mark, editor, description, source_url,
is_formal_source). ADAPT: anchored to Edition (edition_id) per the HFM
canonical model; I2 lineage via parent_version_id self-FK. A version is a
pinned, reproducible reference — nothing resolves to "latest" in Core.
"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class Version(BaseModel):
    """A specific textual version of an Edition (北宋刻本、日本刊本...)."""

    __tablename__ = "versions"

    edition_id: Mapped[str] = mapped_column(
        ForeignKey("editions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属 Edition",
    )
    version_name: Mapped[str] = mapped_column(String(300), nullable=False, comment="版本名称")
    era: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="朝代/时期")
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="版本年份")
    repository: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="收藏机构")
    shelf_mark: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="索书号")
    editor: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="编者/校注者")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="版本描述")
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True, comment="来源链接")
    is_formal_source: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="是否为正式可引用来源",
    )
    parent_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("versions.id", ondelete="SET NULL"),
        nullable=True,
        comment="版本谱系父版本（I2；自引用，须无环）",
    )
