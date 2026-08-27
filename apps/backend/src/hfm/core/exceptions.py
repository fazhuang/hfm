"""Generic exception hierarchy with error codes (migrated Batch 1 asset — ADAPT).

Source: HFB `apps/backend/app/core/exceptions.py` @ `03755b5`.
Adapted: HFM namespace; generic framing without HFB-specific callers.
"""

from __future__ import annotations

from typing import Any


class BaseException(Exception):
    """Root of the application exception hierarchy.

    All application-level exceptions should inherit from this so the global
    error handler can distinguish application errors from unexpected runtime
    errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "APP_ERROR",
        status_code: int = 400,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.metadata = metadata or {}


class DomainException(BaseException):
    """Base for domain-level application exceptions."""


class ValidationException(DomainException):
    """Input data fails validation constraints."""

    def __init__(self, message: str, metadata: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            metadata=metadata,
        )


class NotFoundException(DomainException):
    """Requested resource does not exist."""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            error_code="NOT_FOUND",
            status_code=404,
            metadata={
                "entity_type": entity_type,
                "entity_id": entity_id,
                **(metadata or {}),
            },
        )


class PermissionException(DomainException):
    """Insufficient permissions for the requested action."""

    def __init__(
        self,
        resource: str,
        action: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=f"Permission denied: {resource}.{action}",
            error_code="PERMISSION_DENIED",
            status_code=403,
            metadata={"resource": resource, "action": action, **(metadata or {})},
        )


class ConflictError(DomainException):
    """Request conflicts with current resource state (e.g. optimistic lock)."""

    def __init__(self, message: str, metadata: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            metadata=metadata,
        )
