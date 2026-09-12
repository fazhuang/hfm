"""Research workspace models (P1-12 — P1-RESEARCH, E-12).

Owner-scoped authenticated research state — projects + notes (ADR-05
research namespace; ADR-07 role matrix: STUDENT_RESEARCHER personal
notes, SCHOLAR_RESEARCHER research projects). Ownership always derives
from the authenticated Principal (``owner_id`` = principal.user_id);
client-supplied owner_id is never accepted (deny by default, no IDOR).

Canonical truth stores are reused (Source/SourceRef/Artifact/Version/
Citation/Evidence/Publication/RBAC) — the workspace stores only
owner-scoped research state and introduces no alternate authorization
semantics. Immutable binding: ``owner_id`` is immutable after creation
(I4/I5 stable identity, matching the accepted models).

No clinical semantics: workspace fields are plain research metadata;
nothing here is diagnosis/treatment/prescription/recommendation (AB-14).
"""

from __future__ import annotations

from typing import ClassVar

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates

from hfm.db.base import BaseModel


class ResearchProject(BaseModel):
    """A researcher's project (ADR-07 SCHOLAR_RESEARCHER scope)."""

    __tablename__ = "research_projects"
    __table_args__ = (CheckConstraint("length(title) > 0", name="ck_research_projects_title"),)

    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "owner_id"})

    @validates("owner_id")
    def _validate_owner(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError("owner_id is immutable (I4): create a new project")
        return value

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="所有者（authenticated Principal；客户端不可指定）",
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False, comment="项目标题")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="项目描述")


class ResearchNote(BaseModel):
    """A researcher's personal note (ADR-07 STUDENT_RESEARCHER scope)."""

    __tablename__ = "research_notes"
    __table_args__ = (CheckConstraint("length(content) > 0", name="ck_research_notes_content"),)

    immutable_fields: ClassVar[frozenset[str]] = frozenset({"id", "owner_id"})

    @validates("owner_id")
    def _validate_owner(self, key: str, value: object) -> object:
        current = getattr(self, key, None)
        if self.id is not None and value != current:
            raise ValueError("owner_id is immutable (I4): create a new note")
        return value

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="所有者（authenticated Principal；客户端不可指定）",
    )
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("research_projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="可选所属项目（删除项目级联删除其笔记）",
    )
    title: Mapped[str | None] = mapped_column(String(300), nullable=True, comment="笔记标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="笔记内容")
