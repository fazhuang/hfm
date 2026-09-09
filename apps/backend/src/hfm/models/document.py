"""Content Document model (B05-SG-R2; SG-01 documents)."""

#: Importable DOCUMENT objects carry the B04 DOC-* stable id (SG-02).

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class ContentDocument(BaseModel):
    """Normalized content DOCUMENT (FILE != DOCUMENT != WORK != EDITION)."""

    __tablename__ = "documents"

    edition: Mapped[str | None] = mapped_column(String(300), nullable=True)
    #: SG-02 stable content import identity.
    stable_id: Mapped[str | None] = mapped_column(
        String(120), nullable=True, unique=True, comment="content stable id (unique)"
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    title_normalized: Mapped[str | None] = mapped_column(String(500), nullable=True)
    author_original: Mapped[str | None] = mapped_column(String(300), nullable=True)
    author_normalized: Mapped[str | None] = mapped_column(String(300), nullable=True)
    publication: Mapped[str | None] = mapped_column(String(300), nullable=True)
    year: Mapped[str | None] = mapped_column(String(40), nullable=True)
    doc_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True, server_default="zh")
    source_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source_pages: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    processing_status: Mapped[str | None] = mapped_column(
        String(40), nullable=True, server_default="auto"
    )
    review_status: Mapped[str | None] = mapped_column(
        String(40), nullable=True, server_default="AUTO_EXTRACTED"
    )
