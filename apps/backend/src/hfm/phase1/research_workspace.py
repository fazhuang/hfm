"""Research workspace service (P1-12 — P1-RESEARCH, E-12).

Owner-scoped authenticated research state: projects + notes (ADR-05
research namespace). Authorization follows the frozen ADR-07 §4.1 role
matrix exactly, expressed through capability-matched canonical RBAC codes
(no duplicate role system):

  - projects (create/read/update/delete): ``research:project:*`` —
    SCHOLAR_RESEARCHER only (ADR-07 §4.1: scholarly research projects;
    STUDENT_RESEARCHER is limited to personal notes/bookmarks and is
    DENIED project capability);
  - notes (create/read/update/delete): ``research:note:*`` —
    STUDENT_RESEARCHER and SCHOLAR_RESEARCHER (ADR-07 §4.1 personal
    notes; scholar retains personal notes alongside projects);
  - CONTENT_REVIEWER and anonymous: no research workspace capability
    (deny by default).

Ownership always derives from the authenticated Principal — a
client-supplied owner_id is never accepted (no IDOR). Cross-user access
fails closed (``KeyError`` → 404; no existence oracle). Permission and
ownership are independent and BOTH must pass: a role permission never
bypasses ownership, and an owner match never bypasses a missing role
permission.

Reuses accepted SearchService/ReaderService/Evidence/Citation/Version/
Source/Publication boundaries for richer research access; the workspace
itself stores only owner-scoped private state. No clinical semantics
(AB-14). No HFB runtime dependency; no production import.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.research_workspace import ResearchNote, ResearchProject
from hfm.phase1.auth import Principal

_PAGE_SIZE_MAX = 100

_PROJECT_FIELDS = ("project_id", "title", "description", "created_at")
_NOTE_FIELDS = ("note_id", "project_id", "title", "content", "created_at")


def _validate_paging(page: int, page_size: int) -> None:
    if page < 1 or page_size < 1 or page_size > _PAGE_SIZE_MAX:
        raise ValueError("invalid pagination")


def _require_permission(principal: Principal, code: str) -> None:
    """Deny by default: the principal must hold exactly the required code."""
    if not principal.is_authenticated or not principal.has_permission(code):
        raise PermissionError(f"missing permission: {code}")


class ResearchWorkspaceService:
    """Owner-scoped research projects + notes (E-12 ownership isolation)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------ projects
    async def list_projects(
        self, *, principal: Principal, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """Projects owned by the authenticated principal (deterministic)."""
        _require_permission(principal, "research:project:read")
        _validate_paging(page, page_size)
        base = select(ResearchProject).where(ResearchProject.owner_id == principal.user_id)
        total = _count_result(
            await self.session.execute(select(func.count()).select_from(base.subquery()))
        )
        rows = (
            (
                await self.session.execute(
                    base.order_by(ResearchProject.created_at.desc(), ResearchProject.id)
                    .limit(page_size)
                    .offset((page - 1) * page_size)
                )
            )
            .scalars()
            .all()
        )
        return {
            "projects": [self._serialize_project(p) for p in rows],
            "total": total,
            "page": page,
        }

    async def create_project(
        self, *, principal: Principal, title: str, description: str | None = None
    ) -> dict[str, Any]:
        """Create an owner-scoped research project (canonical permission)."""
        _require_permission(principal, "research:project:create")
        clean_title = (title or "").strip()
        if not clean_title:
            raise ValueError("project title is required")
        project = ResearchProject(
            owner_id=principal.user_id, title=clean_title, description=description
        )
        self.session.add(project)
        await self.session.flush()
        return self._serialize_project(project)

    async def get_project(self, *, principal: Principal, project_id: str) -> dict[str, Any]:
        """Owner-scoped read; other users' projects fail closed (KeyError)."""
        _require_permission(principal, "research:project:read")
        project = await self.session.get(ResearchProject, project_id)
        if project is None or project.owner_id != principal.user_id:
            raise KeyError("project not found")
        return self._serialize_project(project)

    async def update_project(
        self,
        *,
        principal: Principal,
        project_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Owner-scoped update; title stays non-empty."""
        _require_permission(principal, "research:project:update")
        project = await self.session.get(ResearchProject, project_id)
        if project is None or project.owner_id != principal.user_id:
            raise KeyError("project not found")
        if title is not None:
            clean_title = (title or "").strip()
            if not clean_title:
                raise ValueError("project title is required")
            project.title = clean_title
        if description is not None:
            project.description = description
        await self.session.flush()
        return self._serialize_project(project)

    async def delete_project(self, *, principal: Principal, project_id: str) -> None:
        """Owner-scoped delete; notes under the project cascade."""
        _require_permission(principal, "research:project:delete")
        project = await self.session.get(ResearchProject, project_id)
        if project is None or project.owner_id != principal.user_id:
            raise KeyError("project not found")
        await self.session.delete(project)
        await self.session.flush()

    # --------------------------------------------------------------- notes
    async def list_notes(
        self,
        *,
        principal: Principal,
        project_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Notes owned by the principal; optional owner-scoped project filter."""
        _require_permission(principal, "research:note:read")
        _validate_paging(page, page_size)
        base = select(ResearchNote).where(ResearchNote.owner_id == principal.user_id)
        if project_id is not None:
            project = await self.session.get(ResearchProject, project_id)
            if project is None or project.owner_id != principal.user_id:
                raise KeyError("project not found")
            base = base.where(ResearchNote.project_id == project_id)
        total = _count_result(
            await self.session.execute(select(func.count()).select_from(base.subquery()))
        )
        rows = (
            (
                await self.session.execute(
                    base.order_by(ResearchNote.created_at.desc(), ResearchNote.id)
                    .limit(page_size)
                    .offset((page - 1) * page_size)
                )
            )
            .scalars()
            .all()
        )
        return {"notes": [self._serialize_note(n) for n in rows], "total": total, "page": page}

    async def create_note(
        self,
        *,
        principal: Principal,
        content: str,
        project_id: str | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Create an owner-scoped note (optional owner-scoped project binding)."""
        _require_permission(principal, "research:note:create")
        clean_content = (content or "").strip()
        if not clean_content:
            raise ValueError("note content is required")
        if project_id is not None:
            project = await self.session.get(ResearchProject, project_id)
            if project is None or project.owner_id != principal.user_id:
                raise KeyError("project not found")
        note = ResearchNote(
            owner_id=principal.user_id,
            project_id=project_id,
            title=title,
            content=clean_content,
        )
        self.session.add(note)
        await self.session.flush()
        return self._serialize_note(note)

    async def get_note(self, *, principal: Principal, note_id: str) -> dict[str, Any]:
        """Owner-scoped read; other users' notes fail closed (KeyError)."""
        _require_permission(principal, "research:note:read")
        note = await self.session.get(ResearchNote, note_id)
        if note is None or note.owner_id != principal.user_id:
            raise KeyError("note not found")
        return self._serialize_note(note)

    async def update_note(
        self,
        *,
        principal: Principal,
        note_id: str,
        content: str | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Owner-scoped update; content stays non-empty."""
        _require_permission(principal, "research:note:update")
        note = await self.session.get(ResearchNote, note_id)
        if note is None or note.owner_id != principal.user_id:
            raise KeyError("note not found")
        if content is not None:
            clean_content = (content or "").strip()
            if not clean_content:
                raise ValueError("note content is required")
            note.content = clean_content
        if title is not None:
            note.title = title
        await self.session.flush()
        return self._serialize_note(note)

    async def delete_note(self, *, principal: Principal, note_id: str) -> None:
        """Owner-scoped delete."""
        _require_permission(principal, "research:note:delete")
        note = await self.session.get(ResearchNote, note_id)
        if note is None or note.owner_id != principal.user_id:
            raise KeyError("note not found")
        await self.session.delete(note)
        await self.session.flush()

    # -------------------------------------------------------- serialization
    @staticmethod
    def _serialize_project(project: ResearchProject) -> dict[str, Any]:
        return {
            "project_id": project.id,
            "title": project.title,
            "description": project.description,
            "created_at": project.created_at.isoformat(),
        }

    @staticmethod
    def _serialize_note(note: ResearchNote) -> dict[str, Any]:
        return {
            "note_id": note.id,
            "project_id": note.project_id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
        }


def _count_result(result: Any) -> int:
    """Coerce a scalar count; malformed/absent results fail closed to 0."""
    try:
        return int(result.scalar() or 0)
    except (TypeError, ValueError):
        return 0
