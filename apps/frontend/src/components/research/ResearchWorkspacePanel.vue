<script setup lang="ts">
/**
 * ResearchWorkspacePanel (REM-01) — online create + read-back closure for the
 * researcher's own projects and notes, wired to the real P1-12 backend.
 *
 * Existing backend capability only: POST/GET /api/v1/research/projects and
 * /notes. Project management is scholar-scoped (research:project:*); notes are
 * student + scholar (research:note:*). The backend remains the enforcement
 * point — this panel only gates what it offers by the authenticated role.
 */
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import {
  ResearchApiError,
  createResearchNote,
  createResearchProject,
  fetchResearchNotes,
  fetchResearchProjects,
} from '../../services/research'
import type { ResearchNote, ResearchProject } from '../../types/research-workspace'

const store = useAuthStore()

const isScholar = computed(() => store.hasRole('SCHOLAR_RESEARCHER'))
const canWriteNotes = computed(() => store.hasAnyRole(['STUDENT_RESEARCHER', 'SCHOLAR_RESEARCHER']))

// ---- lists ---------------------------------------------------------------
const projects = ref<ResearchProject[]>([])
const notes = ref<ResearchNote[]>([])
const loadingProjects = ref(false)
const loadingNotes = ref(false)
const listError = ref<string | null>(null)

// ---- project form ---------------------------------------------------------
const projectFormOpen = ref(false)
const projectTitle = ref('')
const projectDescription = ref('')
const projectBusy = ref(false)
const projectError = ref<string | null>(null)
const projectSuccess = ref<string | null>(null)

// ---- note form ------------------------------------------------------------
const noteFormOpen = ref(false)
const noteTitle = ref('')
const noteContent = ref('')
const noteProjectId = ref<string>('')
const noteBusy = ref(false)
const noteError = ref<string | null>(null)
const noteSuccess = ref<string | null>(null)

async function loadProjects(): Promise<void> {
  loadingProjects.value = true
  listError.value = null
  try {
    const data = await fetchResearchProjects(store.token)
    projects.value = data.projects
  } catch (err) {
    if (!(err instanceof ResearchApiError)) throw err
    listError.value = `项目列表读取失败 (${err.status})`
    projects.value = []
  } finally {
    loadingProjects.value = false
  }
}

async function loadNotes(): Promise<void> {
  loadingNotes.value = true
  listError.value = null
  try {
    const data = await fetchResearchNotes(store.token)
    notes.value = data.notes
  } catch (err) {
    if (!(err instanceof ResearchApiError)) throw err
    listError.value = `笔记列表读取失败 (${err.status})`
    notes.value = []
  } finally {
    loadingNotes.value = false
  }
}

async function refresh(): Promise<void> {
  await Promise.all([isScholar.value ? loadProjects() : Promise.resolve(), loadNotes()])
}

onMounted(() => {
  void refresh()
})

function friendlyError(err: unknown): string {
  if (err instanceof ResearchApiError) {
    if (err.status === 401) return '会话已失效，请重新登录。'
    if (err.status === 403) return '当前账号没有执行该操作的权限。'
    return err.message || `请求失败 (${err.status})`
  }
  return '网络或服务器错误，请稍后重试。'
}

async function submitProject(): Promise<void> {
  const title = projectTitle.value.trim()
  projectError.value = null
  projectSuccess.value = null
  if (!title) {
    projectError.value = '项目标题不能为空。'
    return
  }
  projectBusy.value = true
  try {
    await createResearchProject(store.token, {
      title,
      description: projectDescription.value.trim() || null,
    })
    projectTitle.value = ''
    projectDescription.value = ''
    projectFormOpen.value = false
    projectSuccess.value = '项目已创建。'
    await loadProjects()
  } catch (err) {
    projectError.value = friendlyError(err)
  } finally {
    projectBusy.value = false
  }
}

async function submitNote(): Promise<void> {
  const content = noteContent.value.trim()
  noteError.value = null
  noteSuccess.value = null
  if (!content) {
    noteError.value = '笔记内容不能为空。'
    return
  }
  noteBusy.value = true
  try {
    await createResearchNote(store.token, {
      content,
      title: noteTitle.value.trim() || null,
      project_id: isScholar.value && noteProjectId.value ? noteProjectId.value : null,
    })
    noteTitle.value = ''
    noteContent.value = ''
    noteProjectId.value = ''
    noteFormOpen.value = false
    noteSuccess.value = '笔记已创建。'
    await loadNotes()
  } catch (err) {
    noteError.value = friendlyError(err)
  } finally {
    noteBusy.value = false
  }
}
</script>

<template>
  <section class="workspace" aria-labelledby="workspace-heading">
    <h2 id="workspace-heading" class="section-title">我的研究</h2>

    <p v-if="listError" class="form-message form-message--error" role="alert">{{ listError }}</p>

    <!-- Projects (scholar capability) -->
    <section v-if="isScholar" aria-labelledby="projects-heading" class="workspace-block">
      <h3 id="projects-heading">研究项目</h3>
      <div class="workspace-toolbar">
        <button
          type="button"
          class="workspace-toggle"
          :aria-expanded="projectFormOpen"
          @click="projectFormOpen = !projectFormOpen"
        >
          {{ projectFormOpen ? '收起表单' : '新增项目' }}
        </button>
        <span v-if="projectSuccess" class="form-message form-message--ok" role="status">{{
          projectSuccess
        }}</span>
      </div>

      <form v-if="projectFormOpen" class="workspace-form" @submit.prevent="submitProject">
        <label for="project-title">
          项目标题 <span aria-hidden="true">（必填）</span>
          <input
            id="project-title"
            v-model="projectTitle"
            type="text"
            maxlength="300"
            required
            autocomplete="off"
          />
        </label>
        <label for="project-description">
          项目描述
          <textarea id="project-description" v-model="projectDescription" rows="3"></textarea>
        </label>
        <p v-if="projectError" class="form-message form-message--error" role="alert">
          {{ projectError }}
        </p>
        <div class="workspace-actions">
          <button type="submit" :disabled="projectBusy" :aria-busy="projectBusy">
            {{ projectBusy ? '创建中…' : '创建项目' }}
          </button>
          <button
            type="button"
            class="workspace-toggle"
            :disabled="projectBusy"
            @click="projectFormOpen = false"
          >
            取消
          </button>
        </div>
      </form>

      <div v-if="loadingProjects" class="workspace-status">正在加载项目…</div>
      <p v-else-if="projects.length === 0" class="workspace-empty">尚无研究项目。</p>
      <ul v-else class="workspace-list">
        <li v-for="project in projects" :key="project.project_id" class="workspace-item">
          <div class="workspace-item__title">{{ project.title }}</div>
          <p v-if="project.description" class="workspace-item__desc">{{ project.description }}</p>
          <p class="workspace-item__meta">项目 ID：{{ project.project_id }}</p>
        </li>
      </ul>
    </section>

    <!-- Notes (student + scholar) -->
    <section v-if="canWriteNotes" aria-labelledby="notes-heading" class="workspace-block">
      <h3 id="notes-heading">我的笔记</h3>
      <div class="workspace-toolbar">
        <button
          type="button"
          class="workspace-toggle"
          :aria-expanded="noteFormOpen"
          @click="noteFormOpen = !noteFormOpen"
        >
          {{ noteFormOpen ? '收起表单' : '新增笔记' }}
        </button>
        <span v-if="noteSuccess" class="form-message form-message--ok" role="status">{{
          noteSuccess
        }}</span>
      </div>

      <form v-if="noteFormOpen" class="workspace-form" @submit.prevent="submitNote">
        <label for="note-title">
          笔记标题
          <input
            id="note-title"
            v-model="noteTitle"
            type="text"
            maxlength="300"
            autocomplete="off"
          />
        </label>
        <label for="note-project">
          关联项目
          <select id="note-project" v-if="isScholar && projects.length > 0" v-model="noteProjectId">
            <option value="">（不关联）</option>
            <option
              v-for="project in projects"
              :key="project.project_id"
              :value="project.project_id"
            >
              {{ project.title }}
            </option>
          </select>
          <input
            id="note-project"
            v-else
            type="text"
            :value="isScholar ? '（无可用项目）' : '（项目管理为学者能力）'"
            disabled
          />
        </label>
        <label for="note-content">
          笔记内容 <span aria-hidden="true">（必填）</span>
          <textarea id="note-content" v-model="noteContent" rows="4" required></textarea>
        </label>
        <p v-if="noteError" class="form-message form-message--error" role="alert">
          {{ noteError }}
        </p>
        <div class="workspace-actions">
          <button type="submit" :disabled="noteBusy" :aria-busy="noteBusy">
            {{ noteBusy ? '创建中…' : '创建笔记' }}
          </button>
          <button
            type="button"
            class="workspace-toggle"
            :disabled="noteBusy"
            @click="noteFormOpen = false"
          >
            取消
          </button>
        </div>
      </form>

      <div v-if="loadingNotes" class="workspace-status">正在加载笔记…</div>
      <p v-else-if="notes.length === 0" class="workspace-empty">尚无笔记。</p>
      <ul v-else class="workspace-list">
        <li v-for="note in notes" :key="note.note_id" class="workspace-item">
          <div class="workspace-item__title">{{ note.title || note.content.slice(0, 60) }}</div>
          <p v-if="note.title" class="workspace-item__desc">{{ note.content }}</p>
          <p class="workspace-item__meta">笔记 ID：{{ note.note_id }}</p>
        </li>
      </ul>
    </section>
  </section>
</template>

<style scoped>
.workspace {
  margin-top: var(--hfm-space-8);
}

.workspace-block {
  margin-top: var(--hfm-space-6);
}

.workspace-toolbar {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-3);
}

.workspace-toggle {
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-interactive);
  cursor: pointer;
  font-weight: 600;
}

.workspace-form {
  display: grid;
  gap: var(--hfm-space-3);
  margin: var(--hfm-space-4) 0;
  max-width: 44rem;
}

.workspace-form label {
  display: grid;
  gap: var(--hfm-space-1);
  font-size: var(--hfm-text-sm);
}

.workspace-form input,
.workspace-form textarea,
.workspace-form select {
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
}

.workspace-actions {
  display: flex;
  gap: var(--hfm-space-2);
}

.workspace-actions button[type='submit'] {
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-citation);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-citation);
  cursor: pointer;
  font-weight: 600;
}

.workspace-actions button[type='submit']:disabled {
  opacity: 0.6;
  cursor: default;
}

.form-message {
  font-size: var(--hfm-text-sm);
}

.form-message--ok {
  color: var(--hfm-color-ok, var(--hfm-color-interactive));
}

.form-message--error {
  color: var(--hfm-color-danger);
}

.workspace-status {
  color: var(--hfm-color-text-muted);
}

.workspace-empty {
  color: var(--hfm-color-text-muted);
}

.workspace-list {
  list-style: none;
  margin: var(--hfm-space-3) 0 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.workspace-item {
  padding: var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
}

.workspace-item__title {
  font-weight: 600;
}

.workspace-item__desc {
  margin: var(--hfm-space-1) 0;
}

.workspace-item__meta {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-xs);
}
</style>
