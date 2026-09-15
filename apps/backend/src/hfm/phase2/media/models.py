"""Media & rights models (P2-05 — P2-C5 media lifecycle, ADR-P2-01).

Registry of media objects: metadata in PostgreSQL, binary bytes in
S3-compatible object storage (never embedded in the relational DB).
Every record carries rights metadata (holder, license basis, restriction,
expiry), a byte hash (sha256) binding the object identity, an
original/derivative linkage (self FK on ``original_object_key``), a
publication state, and an optional deterministic redaction/watermark
token. Publication is fail-closed (P2-05-AC-01): it requires explicit
rights metadata plus a publication grant.

Privacy gating (``HFM-ASSET-PRESENTATION-POLICY.md`` §4) is a schema
invariant here rather than a convention: P3 material is never published,
a P2 *original* is never published (only its redacted derivative may be),
a P2/P3 row never carries ``publication_permission``, and the
derivative-only grant cannot be set on a row without an original.
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


class PrivacyClass(str):
    """Privacy class (``HFM-ASSET-PRESENTATION-POLICY.md`` §4).

    ``P0`` ordinary public content · ``P1`` professional / academic /
    public-identity information · ``P2`` personal information requiring
    redaction (certificate numbers, signatures, ID numbers, private
    contact details) · ``P3`` sensitive material that never enters the
    public projection.
    """

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


#: Classes gated out of direct publication: P2 requires a redacted public
#: derivative, P3 is never published at all.
GATED_PRIVACY_CLASSES: frozenset[str] = frozenset({PrivacyClass.P2, PrivacyClass.P3})


class AccessScope(str):
    """Which section of the platform an asset belongs to.

    Orthogonal to :class:`MediaAssetState`: scope says *who the audience is*,
    state says *whether the asset is ready for that audience*. A 非遗
    certificate is ``PUBLIC`` scope while still ``draft`` — it is portal
    material that has not been redacted yet.

    The default is :attr:`RESEARCH`, not :attr:`PUBLIC`, so the boundary
    fails closed: a new asset is invisible to the public portal until someone
    deliberately promotes it.
    """

    PUBLIC = "public"
    RESEARCH = "research"


#: Default scope for a newly registered asset (fail-closed).
DEFAULT_ACCESS_SCOPE = AccessScope.RESEARCH


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
        CheckConstraint(
            "privacy_class IN ('P0', 'P1', 'P2', 'P3')",
            name="ck_media_assets_privacy_class",
        ),
        CheckConstraint(
            "privacy_class <> 'P3' OR publication_state <> 'published'",
            name="ck_media_assets_p3_never_published",
        ),
        CheckConstraint(
            "privacy_class <> 'P2' OR original_object_key IS NOT NULL "
            "OR publication_state <> 'published'",
            name="ck_media_assets_p2_original_never_published",
        ),
        CheckConstraint(
            "privacy_class NOT IN ('P2', 'P3') OR NOT publication_permission",
            name="ck_media_assets_gated_never_permitted",
        ),
        CheckConstraint(
            "NOT derivative_publication_permission OR original_object_key IS NOT NULL",
            name="ck_media_assets_derivative_grant",
        ),
        CheckConstraint(
            "access_scope IN ('public', 'research')",
            name="ck_media_assets_access_scope",
        ),
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

    #: Derivative-only publication grant (policy §4.1). A P2 original can
    #: never carry ``publication_permission``, so the redacted derivative
    #: carries its own grant instead — the original stays sealed. A check
    #: constraint forbids setting this on a row without an original.
    derivative_publication_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    #: Privacy class governing publication eligibility (policy §4).
    privacy_class: Mapped[str] = mapped_column(String(2), nullable=False, default=PrivacyClass.P0)

    #: Which section of the platform this asset belongs to (portal vs
    #: research). Independent of ``publication_state``; defaults to the
    #: fail-closed value so nothing reaches the portal unasked.
    access_scope: Mapped[str] = mapped_column(
        String(8), nullable=False, default=DEFAULT_ACCESS_SCOPE, server_default="research"
    )

    #: Customer asset-register identifier (``HFM-A000013``). Joins this row to
    #: ``documents.source_asset_id``, which speaks the register's language
    #: while ``id`` is a UUID. Nullable: not every future asset comes from the
    #: register.
    ledger_id: Mapped[str | None] = mapped_column(String(16), nullable=True, unique=True)

    publication_state: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MediaAssetState.DRAFT
    )

    #: Deterministic redaction/watermark token (P2-05-AC-04).
    redaction_token: Mapped[str | None] = mapped_column(String(200), nullable=True)

    #: Free-form provenance note (source snapshot, origin). Never treated as
    #: a rights grant by itself.
    provenance: Mapped[str | None] = mapped_column(Text, nullable=True)
