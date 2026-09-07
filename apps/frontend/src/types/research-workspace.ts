/**
 * Research workspace (P1-12) types (REM-01 — project & note write closure).
 *
 * Mirrors the real backend contract (ResearchWorkspaceService /
 * apps/backend/src/hfm/phase1/research_workspace.py):
 *   project {project_id,title,description,created_at}
 *   note    {note_id,project_id,title,content,created_at}
 * Responses arrive inside the standard api_response envelope ({success,data,…}).
 * This is the only client-side shape — no second data model.
 */

export interface ResearchProject {
  project_id: string
  title: string
  description: string | null
  created_at: string
}

export interface ResearchNote {
  note_id: string
  project_id: string | null
  title: string | null
  content: string
  created_at: string
}

export interface ResearchProjectList {
  projects: ResearchProject[]
  total: number
  page: number
}

export interface ResearchNoteList {
  notes: ResearchNote[]
  total: number
  page: number
}
