"""ContentArtifact model (P1-01 — canonical content admission core).

Implements the Phase 1 architecture layer `Source → Artifact → Version →
Provenance → …` admission boundary (AB-06) and the P1-01 acceptance
criterion: invalid provenance/rights is rejected, admitted content carries
source/version state, and metadata-only admission is impossible.

  - canonical ownership: HFM-owned artifact identity (I5) with an immutable
    content_hash (integrity) and source binding (provenance);
  - admission boundary: admission_state ∈ {submitted, admitted, rejected} —
    deliberately distinct from APPROVED / PUBLISHED (publication is P1-09);
  - fail-closed: the repository admission gate rejects malformed/incomplete
    inputs and records a rejection_reason; unknown rights or failed
    provenance never become admitted content (AB invariant 5);
  - no publication semantics: no approved/published/visible fields.

Rights classification mirrors the CA-10 media rights classes from
HFM-CONTENT-ASSET-REQUEST-REGISTER-v1.md; UNKNOWN is never admitted.
"""

from __future__ import annotations

import enum
from typing import ClassVar

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class ContentAdmissionState(enum.StrEnum):
    """Admission lifecycle state (NOT a publication state — P1-09)."""

    SUBMITTED = "submitted"
    ADMITTED = "admitted"
    REJECTED = "rejected"


class ProvenanceStatus(enum.StrEnum):
    """Provenance verification state of the source/artifact chain."""

    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class RightsStatus(enum.StrEnum):
    """Media/content rights class (CA-10 register; UNKNOWN never admitted)."""

    PUBLIC_DOMAIN = "public_domain"
    CUSTOMER_OWNED = "customer_owned"
    LICENSED = "licensed"
    THIRD_PARTY_PERMISSION_REQUIRED = "third_party_permission_required"
    UNKNOWN = "unknown"


class ValidationResult(enum.StrEnum):
    """Admission validation result (integrity/schema validation)."""

    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"


_ADMISSION_VALUES = ", ".join(f"'{s.value}'" for s in ContentAdmissionState)
_PROVENANCE_VALUES = ", ".join(f"'{p.value}'" for p in ProvenanceStatus)
_RIGHTS_VALUES = ", ".join(f"'{r.value}'" for r in RightsStatus)
_VALIDATION_VALUES = ", ".join(f"'{v.value}'" for v in ValidationResult)


class ContentArtifact(BaseModel):
    """An admitted content item bound to a Source and (optionally) a Version."""

    __tablename__ = "content_artifacts"
    __table_args__ = (
        UniqueConstraint("source_id", "content_hash", name="uq_content_artifacts_source_hash"),
        CheckConstraint(
            f"admission_state IN ({_ADMISSION_VALUES})",
            name="ck_content_artifacts_admission_state",
        ),
        CheckConstraint(
            f"provenance_status IN ({_PROVENANCE_VALUES})",
            name="ck_content_artifacts_provenance_status",
        ),
        CheckConstraint(
            f"rights_status IN ({_RIGHTS_VALUES})",
            name="ck_content_artifacts_rights_status",
        ),
        CheckConstraint(
            f"validation_result IN ({_VALIDATION_VALUES})",
            name="ck_content_artifacts_validation_result",
        ),
        CheckConstraint(
            "content_hash IS NOT NULL AND length(content_hash) > 0"
            " OR admission_state != 'admitted'",
            name="ck_content_artifacts_content_hash_present",
        ),
        CheckConstraint(
            "source_id IS NOT NULL OR admission_state != 'admitted'",
            name="ck_content_artifacts_source_present",
        ),
        CheckConstraint(
            "admission_state != 'rejected' OR rejection_reason IS NOT NULL",
            name="ck_content_artifacts_rejection_has_reason",
        ),
    )

    #: source binding, integrity digest and admission disposition are
    #: immutable once persisted (I4) — a corrected admission is a new record.
    immutable_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "id",
            "source_id",
            "content_hash",
            "admission_state",
            "rejection_reason",
            "version_id",
            "created_by",
        }
    )

    @validates(
        "source_id",
        "content_hash",
        "admission_state",
        "rejection_reason",
        "version_id",
        "created_by",
    )
    def _validate_immutable(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        # id-based guard: once persisted, any change from the loaded state is rejected
        if self.id is not None and value != current:
            raise ValueError(f"{key} is immutable (I4): create a new artifact admission")
        return value

    source_id: Mapped[str | None] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="来源/所有者身份（ADMITTED 必备 provenance — AB-06；REJECTED 记录可空）",
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="内容完整性哈希（canonical sha256；禁止 metadata-only admission）",
    )
    format: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="MIME/载体格式")
    provenance_status: Mapped[ProvenanceStatus] = mapped_column(
        String(20),
        nullable=False,
        default=ProvenanceStatus.PENDING,
        server_default="pending",
        comment="溯源状态: pending/verified/failed",
    )
    rights_status: Mapped[RightsStatus] = mapped_column(
        String(40),
        nullable=False,
        default=RightsStatus.UNKNOWN,
        server_default="unknown",
        comment="权利分类（CA-10）: public_domain/customer_owned/licensed/"
        "third_party_permission_required/unknown",
    )
    validation_result: Mapped[ValidationResult] = mapped_column(
        String(20),
        nullable=False,
        default=ValidationResult.PENDING,
        server_default="pending",
        comment="校验结果: pending/pass/fail",
    )
    admission_state: Mapped[ContentAdmissionState] = mapped_column(
        String(20),
        nullable=False,
        default=ContentAdmissionState.SUBMITTED,
        server_default="submitted",
        comment="准入状态（非发布状态 — P1-09）: submitted/admitted/rejected",
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="拒绝原因（fail-closed rejection log）"
    )
    version_id: Mapped[str | None] = mapped_column(
        ForeignKey("versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="版本绑定（admitted content 的 version state — 可选）",
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="provenance 录入者引用占位（CA-026 BRIDGE_FROZEN；无 User FK）",
    )
