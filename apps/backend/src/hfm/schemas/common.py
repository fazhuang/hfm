"""Common schema types shared across HFM (migrated Batch 2 asset — PORT).

Source: HFB `apps/backend/app/schemas/common.py` @ `03755b5`.
Generic pagination primitives; no domain coupling.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Pagination metadata envelope."""

    page: int
    limit: int
    total: int
    total_pages: int
