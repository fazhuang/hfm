/**
 * REM-01 — research workspace project/note write closure tests.
 *
 * Proves the real API wiring (envelope unwrap, auth header, error mapping)
 * and the create UI behavior (form render, validation, submit → real fetch,
 * success read-back reload, failure handling) for projects and notes.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import ResearchWorkspacePanel from '../components/research/ResearchWorkspacePanel.vue'
import {
  ResearchApiError,
  createResearchNote,
  createResearchProject,
  fetchResearchNotes,
  fetchResearchProjects,
} from '../services/research'
import { useAuthStore } from '../stores/auth'
import type { AuthUser } from '../types/auth'

const PROJECT = {
  project_id: 'p1',
  title: '皇甫谧针灸甲乙经考',
  description: '版本源流研究',
  created_at: '2026-09-07T00:00:00Z',
}
const NOTE = {
  note_id: 'n1',
  project_id: 'p1',
  title: '待考条目',
  content: '考据一则',
  created_at: '2026-09-07T00:00:00Z',
}

function envelope(data: unknown) {
  return { success: true, timestamp: 't', message: 'ok', data }
}

function okResponse(data: unknown) {
  return { ok: true, status: 200, json: async () => envelope(data) }
}

function user(roles: AuthUser['roles']): AuthUser {
  return { id: 'u1', roles, permissions: [] }
}

function makeHarness(roles: AuthUser['roles']) {
  const pinia = createPinia()
  setActivePinia(pinia)
  const store = useAuthStore()
  store.$patch({ token: 'token-1', user: user(roles) })
  return pinia
}

function mountPanel(pinia: ReturnType<typeof createPinia>) {
  return mount(ResearchWorkspacePanel, { attachTo: document.body, global: { plugins: [pinia] } })
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('research service — real API contract', () => {
  it('createResearchProject posts with bearer auth and unwraps the envelope', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse(PROJECT))
    vi.stubGlobal('fetch', fetchMock)
    const created = await createResearchProject('token-1', { title: PROJECT.title })
    expect(created.project_id).toBe('p1')
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/api/v1/research/projects')
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer token-1')
    expect(JSON.parse(String(init.body))).toEqual({ title: PROJECT.title, description: null })
    vi.unstubAllGlobals()
  })

  it('fetchResearchProjects GETs the list and unwraps data', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ projects: [PROJECT], total: 1, page: 1 }))
    vi.stubGlobal('fetch', fetchMock)
    const data = await fetchResearchProjects('token-1')
    expect(data.projects).toHaveLength(1)
    expect((fetchMock.mock.calls[0] as [string])[0]).toContain('/api/v1/research/projects')
    vi.unstubAllGlobals()
  })

  it('createResearchNote posts content + optional project/title', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse(NOTE))
    vi.stubGlobal('fetch', fetchMock)
    const created = await createResearchNote('token-1', { content: NOTE.content, project_id: 'p1', title: NOTE.title })
    expect(created.note_id).toBe('n1')
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(JSON.parse(String(init.body))).toEqual({ content: NOTE.content, project_id: 'p1', title: NOTE.title })
    vi.unstubAllGlobals()
  })

  it('fetchResearchNotes sends project_id filter when provided', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ notes: [NOTE], total: 1, page: 1 }))
    vi.stubGlobal('fetch', fetchMock)
    await fetchResearchNotes('token-1', 'p1')
    expect((fetchMock.mock.calls[0] as [string])[0]).toContain('project_id=p1')
    vi.unstubAllGlobals()
  })

  it('backend rejection surfaces ResearchApiError with status + message', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ success: false, data: null, message: 'project title is required' }),
      }),
    )
    await expect(createResearchProject('token-1', { title: 'x' })).rejects.toMatchObject({
      name: 'ResearchApiError',
      status: 400,
      message: expect.stringContaining('project title is required'),
    } as Partial<ResearchApiError>)
    vi.unstubAllGlobals()
  })
})

describe('project create UI', () => {
  it('scholar sees projects section; valid submit posts and read-back shows the project', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(okResponse({ projects: [], total: 0, page: 1 })) // mount load
      .mockResolvedValueOnce(okResponse({ notes: [], total: 0, page: 1 }))
      .mockResolvedValueOnce(okResponse(PROJECT)) // create
      .mockResolvedValueOnce(okResponse({ projects: [PROJECT], total: 1, page: 1 })) // reload
    vi.stubGlobal('fetch', fetchMock)
    const pinia = makeHarness(['SCHOLAR_RESEARCHER'])
    const wrapper = mountPanel(pinia)
    await wrapper.get('button.workspace-toggle').trigger('click') // open project form
    await vi.waitFor(() => expect(wrapper.find('#project-title').exists()).toBe(true))

    await wrapper.get('#project-title').setValue('皇甫谧针灸甲乙经考')
    await wrapper.get('#project-description').setValue('版本源流研究')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.text()).toContain('项目已创建'))
    await vi.waitFor(() => expect(wrapper.text()).toContain('皇甫谧针灸甲乙经考'))
    const postCalls = fetchMock.mock.calls.filter((c) => c[0] === '/api/v1/research/projects')
    expect(postCalls).toHaveLength(1)
    expect(String((postCalls[0][1] as RequestInit).method)).toBe('POST')
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('empty title fails client validation without a network call', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(okResponse({ projects: [], total: 0, page: 1 }))
      .mockResolvedValueOnce(okResponse({ notes: [], total: 0, page: 1 }))
    vi.stubGlobal('fetch', fetchMock)
    const pinia = makeHarness(['SCHOLAR_RESEARCHER'])
    const wrapper = mountPanel(pinia)
    await wrapper.get('button.workspace-toggle').trigger('click')
    await vi.waitFor(() => expect(wrapper.find('#project-title').exists()).toBe(true))
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.text()).toContain('项目标题不能为空'))
    const postCalls = fetchMock.mock.calls.filter((c) => c[0] === '/api/v1/research/projects')
    expect(postCalls).toHaveLength(0)
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('server rejection shows the backend error and keeps form state', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(okResponse({ projects: [], total: 0, page: 1 })) // mount projects
      .mockResolvedValueOnce(okResponse({ notes: [], total: 0, page: 1 })) // mount notes
      .mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ success: false, data: null, message: 'project title is required' }),
      }) // POST rejected
    vi.stubGlobal('fetch', fetchMock)
    const pinia = makeHarness(['SCHOLAR_RESEARCHER'])
    const wrapper = mountPanel(pinia)
    await wrapper.get('button.workspace-toggle').trigger('click')
    await vi.waitFor(() => expect(wrapper.find('#project-title').exists()).toBe(true))
    await wrapper.get('#project-title').setValue('still rejected')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.text()).toContain('project title is required'))
    expect(wrapper.text()).not.toContain('项目已创建')
    expect((wrapper.get('#project-title').element as HTMLInputElement).value).toBe('still rejected')
    wrapper.unmount()
    vi.unstubAllGlobals()
  })
})

describe('note create UI', () => {
  it('student sees notes (not projects); valid submit posts and read-back shows the note', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(okResponse({ notes: [], total: 0, page: 1 })) // mount: no projects call for student
      .mockResolvedValueOnce(okResponse(NOTE)) // create
      .mockResolvedValueOnce(okResponse({ notes: [NOTE], total: 1, page: 1 })) // reload
    vi.stubGlobal('fetch', fetchMock)
    const pinia = makeHarness(['STUDENT_RESEARCHER'])
    const wrapper = mountPanel(pinia)
    await wrapper.get('button.workspace-toggle').trigger('click') // open note form
    await vi.waitFor(() => expect(wrapper.find('#note-content').exists()).toBe(true))
    expect(wrapper.text()).not.toContain('研究项目')
    await wrapper.get('#note-content').setValue('考据一则')
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.text()).toContain('笔记已创建'))
    await vi.waitFor(() => expect(wrapper.text()).toContain('考据一则'))
    const post = fetchMock.mock.calls.find(
      (c) => c[0] === '/api/v1/research/notes' && (c[1] as RequestInit).method === 'POST',
    )
    expect(post).toBeTruthy()
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('empty note content fails client validation without a network call', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(okResponse({ notes: [], total: 0, page: 1 }))
    vi.stubGlobal('fetch', fetchMock)
    const pinia = makeHarness(['STUDENT_RESEARCHER'])
    const wrapper = mountPanel(pinia)
    await wrapper.get('button.workspace-toggle').trigger('click')
    await vi.waitFor(() => expect(wrapper.find('#note-content').exists()).toBe(true))
    await wrapper.get('form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.text()).toContain('笔记内容不能为空'))
    const posts = fetchMock.mock.calls.filter(
      (c) => c[0] === '/api/v1/research/notes' && (c[1] as RequestInit).method === 'POST',
    )
    expect(posts).toHaveLength(0)
    wrapper.unmount()
    vi.unstubAllGlobals()
  })
})
