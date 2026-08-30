"""Media & rights models (P2-05 — P2-C5 media lifecycle, ADR-P2-01).

Registry of media objects: metadata in PostgreSQL, binary bytes in
S3-compatible object storage (never embedded in the relational DB).
Every record carries rights metadata (holder, license basis, restriction,
expiry), a byte hash (sha256) binding the object identity, an
original/derivative linkage (self FK on ``original_object_key``), a
publication state, and an optional deterministic redaction/watermark
token. Publication is fail-closed (P2-05-AC-01): it requires explicit
rights metadata plus ``publication_permission``.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hfm.db.base import BaseModel


class MediaAssetState(str):
    """Publication state of a media object."""

    DRAFT = "draft"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"


class MediaAsset(BaseModel):
    """One media object (original or public derivative)."""

    __tablename__ = "media_assets"
    __table_args__ = (
        CheckConstraint(
            "publication_state IN ('draft', 'published', 'withdrawn')",
            name="ck_media_assets_state",
        ),
        CheckConstraint("byte_size >= 0", name="ck_media_assets_byte_size"),
        CheckConstraint("length(object_key) > 0", name="ck_media_assets_object_key"),
    )

    object_key: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    original_object_key: Mapped[str | None] = mapped_column(
        String(500), ForeignKey("media_assets.object_key", ondelete="RESTRICT"), nullable=True
    )
    mime_type: Mapped[str] = mapped_column(String(200), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    #: Rights metadata (ADR-P2-01) — publication is fail-closed without these.
    rights_holder: Mapped[str] = mapped_column(String(300), nullable=False)
    license_basis: Mapped[str] = mapped_column(String(300), nullable=False)
    restriction: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rights_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    publication_permission: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    publication_state: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MediaAssetState.DRAFT
    )

    #: Deterministic redaction/watermark token (P2-05-AC-04).
    redaction_token: Mapped[str | None] = mapped_column(String(200), nullable=True)

    #: Free-form provenance note (source snapshot, origin). Never treated as
    #: a rights grant by itself.
    provenance: Mapped[str | None] = mapped_column(Text, nullable=True)
