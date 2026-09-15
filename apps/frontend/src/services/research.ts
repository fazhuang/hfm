/**
 * Research workspace API client (REM-01 — project & note write closure).
 *
 * Real, authenticated calls to the existing P1-12 backend endpoints
 * (POST/GET /api/v1/research/projects and /notes) under the standard
 * api_response envelope. The caller supplies the in-memory Bearer token from
 * the auth store; server-side RBAC remains the enforcement point
 * (research:project:* = scholar; research:note:* = scholar + student).
 */
import type {
  ResearchAnnotation,
  ResearchAnnotationList,
  ResearchNote,
  ResearchNoteList,
  ResearchProject,
  ResearchProjectList,
} from '../types/research-workspace'

/** Error carrying the HTTP status and the backend message when available. */
export class ResearchApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ResearchApiError'
    this.status = status
  }
}

interface Envelope<T> {
  success?: boolean
  data?: T
  message?: string
}

async function researchRequest<T>(
  path: string,
  init: { method?: string; token: string | null; body?: unknown },
): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (init.token) headers.Authorization = `Bearer ${init.token}`
  const response = await fetch(path, {
    method: init.method ?? 'GET',
    headers,
    body: init.body !== undefined ? JSON.stringify(init.body) : undefined,
  })
  let payload: unknown = null
  try {
    payload = await response.json()
  } catch {
    payload = null
  }
  if (!response.ok) {
    const message =
      payload && typeof payload === 'object' && 'message' in payload
        ? String((payload as { message?: unknown }).message ?? '')
        : ''
    throw new ResearchApiError(
      message
        ? `research request failed: ${message}`
        : `research request failed: ${response.status}`,
      response.status,
    )
  }
  const envelope = payload as Envelope<T>
  if (envelope === null || typeof envelope !== 'object' || envelope.data === undefined) {
    throw new ResearchApiError('research response missing envelope data', response.status)
  }
  return envelope.data
}

/** Projects owned by the authenticated researcher (research:project:read). */
export function fetchResearchProjects(token: string | null): Promise<ResearchProjectList> {
  return researchRequest<ResearchProjectList>('/api/v1/research/projects?page=1&page_size=100', {
    method: 'GET',
    token,
  })
}

/** Create an owner-scoped research project (research:project:create). */
export function createResearchProject(
  token: string | null,
  body: { title: string; description?: string | null },
): Promise<ResearchProject> {
  return researchRequest<ResearchProject>('/api/v1/research/projects', {
    method: 'POST',
    token,
    body: { title: body.title, description: body.description ?? null },
  })
}

/** Notes owned by the researcher, optionally inside one of their projects. */
export function fetchResearchNotes(
  token: string | null,
  projectId?: string | null,
): Promise<ResearchNoteList> {
  const suffix = projectId ? `?project_id=${encodeURIComponent(projectId)}` : ''
  return researchRequest<ResearchNoteList>(`/api/v1/research/notes${suffix}`, {
    method: 'GET',
    token,
  })
}

/** Create an owner-scoped note (research:note:create; student + scholar). */
export function createResearchNote(
  token: string | null,
  body: { content: string; project_id?: string | null; title?: string | null },
): Promise<ResearchNote> {
  return researchRequest<ResearchNote>('/api/v1/research/notes', {
    method: 'POST',
    token,
    body: { content: body.content, project_id: body.project_id ?? null, title: body.title ?? null },
  })
}

/** Annotations owned by the researcher, optionally filtered by passage (P4). */
export function fetchResearchAnnotations(
  token: string | null,
  passageId?: string | null,
): Promise<ResearchAnnotationList> {
  const suffix = passageId ? `?passage_id=${encodeURIComponent(passageId)}` : ''
  return researchRequest<ResearchAnnotationList>(`/api/v1/research/annotations${suffix}`, {
    method: 'GET',
    token,
  })
}

/** Create an owner-scoped highlight annotation on a passage (P4). */
export function createResearchAnnotation(
  token: string | null,
  body: {
    passage_id: string
    note?: string | null
    project_id?: string | null
    quote_text?: string | null
    start_offset?: number | null
    end_offset?: number | null
  },
): Promise<ResearchAnnotation> {
  return researchRequest<ResearchAnnotation>('/api/v1/research/annotations', {
    method: 'POST',
    token,
    body: {
      passage_id: body.passage_id,
      note: body.note ?? null,
      project_id: body.project_id ?? null,
      quote_text: body.quote_text ?? null,
      start_offset: body.start_offset ?? null,
      end_offset: body.end_offset ?? null,
    },
  })
}

/** Delete an owner-scoped highlight annotation (P4). */
export function deleteResearchAnnotation(
  token: string | null,
  annotationId: string,
): Promise<{ ok: boolean }> {
  return researchRequest<{ ok: boolean }>(
    `/api/v1/research/annotations/${encodeURIComponent(annotationId)}`,
    { method: 'DELETE', token },
  )
}
