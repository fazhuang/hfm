<script setup lang="ts">
/**
 * JiayiStructureView — P4 research reader: 《针灸甲乙经》篇章在线阅读 + 标注.
 *
 * Live reader over the published chapter/passage structure
 * (GET /public/works/{work}/structure → 卷 → 篇 → 段). Clicking a 段 loads its
 * full text via the versioned reader (GET /public/reader/resolve?passage_id=).
 *
 * When authenticated, each 段 exposes a highlight-annotation surface bound to
 * the owner-scoped P4 backend (POST/GET/DELETE /research/annotations,
 * research:note:* RBAC). Citation is the canonical locator formatted as
 * 《作品》卷·篇·第N段 — a reproducible reference, never clinical (AB-14).
 */
import { computed, onMounted, ref } from 'vue'
import { fetchPublicWorkStructure } from '../../services/api'
import { resolvePassageById } from '../../services/reader'
import {
  createResearchAnnotation,
  deleteResearchAnnotation,
  fetchResearchAnnotations,
} from '../../services/research'
import { useAuthStore } from '../../stores/auth'
import type { StructureChapter, StructurePassage, WorkStructure } from '../../types/reader'
import type { ResearchAnnotation } from '../../types/research-workspace'

defineOptions({ name: 'JiayiStructureView' })

const JIAYI_WORK_ID = 'WORK-JIAYI'

const auth = useAuthStore()

const structure = ref<WorkStructure | null>(null)
const loading = ref(false)
const error = ref('')

const expanded = ref<Record<string, boolean>>({})
const selectedPassageId = ref<string | null>(null)
const selectedChapter = ref<StructureChapter | null>(null)
const selectedVolume = ref<StructureChapter | null>(null)
const passageText = ref<string | null>(null)
const passageLoading = ref(false)

const annotations = ref<ResearchAnnotation[]>([])
const annotationLoading = ref(false)
const annotationNote = ref('')
const annotationError = ref('')
const annotationSaving = ref(false)

const isAuthenticated = computed(() => auth.isAuthenticated)

async function loadStructure(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    structure.value = await fetchPublicWorkStructure(JIAYI_WORK_ID)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载篇章结构失败'
  } finally {
    loading.value = false
  }
}

function toggle(id: string): void {
  expanded.value[id] = !expanded.value[id]
}

async function selectPassage(
  passage: StructurePassage,
  chapter: StructureChapter,
  volume: StructureChapter,
): Promise<void> {
  selectedPassageId.value = passage.passage_id
  selectedChapter.value = chapter
  selectedVolume.value = volume
  passageText.value = null
  passageLoading.value = true
  annotationNote.value = ''
  annotationError.value = ''
  try {
    const resolved = await resolvePassageById(passage.passage_id)
    passageText.value = resolved.quotation
  } catch (err) {
    passageText.value = null
    annotationError.value = err instanceof Error ? err.message : '加载正文失败'
  } finally {
    passageLoading.value = false
  }
  if (isAuthenticated.value) await loadAnnotations(passage.passage_id)
}

async function loadAnnotations(passageId: string): Promise<void> {
  if (!auth.token) return
  annotationLoading.value = true
  try {
    const data = await fetchResearchAnnotations(auth.token, passageId)
    annotations.value = data.annotations
  } catch {
    annotations.value = []
  } finally {
    annotationLoading.value = false
  }
}

async function saveAnnotation(): Promise<void> {
  if (!auth.token || !selectedPassageId.value) return
  const note = annotationNote.value.trim()
  if (!note) {
    annotationError.value = '批注内容不能为空'
    return
  }
  annotationSaving.value = true
  annotationError.value = ''
  try {
    await createResearchAnnotation(auth.token, {
      passage_id: selectedPassageId.value,
      note,
    })
    annotationNote.value = ''
    await loadAnnotations(selectedPassageId.value)
  } catch (err) {
    annotationError.value = err instanceof Error ? err.message : '保存标注失败'
  } finally {
    annotationSaving.value = false
  }
}

async function removeAnnotation(annotationId: string): Promise<void> {
  if (!auth.token || !selectedPassageId.value) return
  try {
    await deleteResearchAnnotation(auth.token, annotationId)
    await loadAnnotations(selectedPassageId.value)
  } catch (err) {
    annotationError.value = err instanceof Error ? err.message : '删除标注失败'
  }
}

/** Canonical citation: 《作品》卷·篇·第N段. */
const citation = computed<string>(() => {
  if (!selectedChapter.value || !selectedPassageId.value) return ''
  const workTitle = structure.value?.title ?? '针灸甲乙经'
  const volumeTitle = selectedVolume.value?.title ?? ''
  const order = passageOrder(selectedChapter.value, selectedPassageId.value)
  return `《${workTitle}》${volumeTitle}·${selectedChapter.value.title}·第${order}段`
})

function passageOrder(chapter: StructureChapter, passageId: string): number {
  return chapter.passages?.find((x) => x.passage_id === passageId)?.order ?? 0
}

onMounted(loadStructure)
</script>

<template>
  <article class="structure" aria-labelledby="structure-title">
    <header class="structure__header">
      <h1 id="structure-title" class="structure__title">
        {{ structure?.title ?? '《针灸甲乙经》' }} · 篇章阅读
      </h1>
      <p class="structure__subtitle">
        在线阅读《针灸甲乙经》十二卷一百三十七篇（公有领域·宋校本），可划选标注、生成引文。
      </p>
    </header>

    <p v-if="loading" class="structure__state">正在加载篇章结构…</p>
    <p v-if="error" class="structure__state structure__state--error">{{ error }}</p>

    <div v-if="structure" class="structure__layout">
      <!-- 卷 → 篇 → 段 tree -->
      <nav class="structure__tree" aria-label="篇章目录">
        <section v-for="volume in structure.chapters" :key="volume.chapter_id" class="volume">
          <button
            type="button"
            class="volume__toggle"
            :aria-expanded="!!expanded[volume.chapter_id]"
            @click="toggle(volume.chapter_id)"
          >
            <span class="volume__marker">{{ expanded[volume.chapter_id] ? '−' : '+' }}</span>
            <span class="volume__title">{{ volume.title }}</span>
          </button>

          <ul v-if="expanded[volume.chapter_id]" class="pian">
            <li v-for="pian in volume.children ?? []" :key="pian.chapter_id" class="pian__item">
              <div class="pian__title">{{ pian.title }}</div>
              <ol class="duan">
                <li v-for="p in pian.passages ?? []" :key="p.passage_id" class="duan__item">
                  <button
                    type="button"
                    class="duan__link"
                    :class="{ 'duan__link--active': selectedPassageId === p.passage_id }"
                    @click="selectPassage(p, pian, volume)"
                  >
                    第{{ p.order }}段 · {{ p.preview }}
                  </button>
                </li>
              </ol>
            </li>
          </ul>
        </section>
      </nav>

      <!-- passage detail -->
      <section class="structure__detail" aria-live="polite">
        <template v-if="selectedPassageId">
          <p v-if="passageLoading" class="structure__state">正在加载正文…</p>
          <blockquote v-else-if="passageText" class="passage__text">
            {{ passageText }}
          </blockquote>

          <div v-if="citation" class="citation">
            <span class="citation__label">引文</span>
            <code class="citation__value">{{ citation }}</code>
          </div>

          <!-- annotations -->
          <div v-if="isAuthenticated" class="annotations">
            <h2 class="annotations__heading">标注</h2>
            <p v-if="annotationLoading" class="structure__state">正在加载标注…</p>
            <ul v-else class="annotations__list">
              <li v-for="a in annotations" :key="a.annotation_id" class="annotations__item">
                <p class="annotations__note">{{ a.note }}</p>
                <button
                  type="button"
                  class="annotations__remove"
                  @click="removeAnnotation(a.annotation_id)"
                >
                  删除
                </button>
              </li>
              <li v-if="annotations.length === 0" class="annotations__empty">暂无标注</li>
            </ul>

            <form class="annotations__form" @submit.prevent="saveAnnotation">
              <label class="annotations__label" for="annotation-note">添加批注</label>
              <textarea
                id="annotation-note"
                v-model="annotationNote"
                class="annotations__input"
                rows="3"
                placeholder="在此写下对这一段落的批注（历史考证，非临床建议）"
              ></textarea>
              <button type="submit" class="annotations__submit" :disabled="annotationSaving">
                {{ annotationSaving ? '保存中…' : '保存标注' }}
              </button>
              <p v-if="annotationError" class="annotations__error">{{ annotationError }}</p>
            </form>
          </div>
          <p v-else class="structure__state">
            <RouterLink to="/login">登录</RouterLink> 后可对段落做高亮标注。
          </p>
        </template>

        <p v-else class="structure__state structure__state--empty">
          从左侧目录选择一段落查看正文。
        </p>
      </section>
    </div>
  </article>
</template>

<style scoped>
.structure {
  max-width: 72rem;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}
.structure__header {
  margin-bottom: 1.25rem;
}
.structure__title {
  font-size: 1.5rem;
  margin: 0 0 0.25rem;
}
.structure__subtitle {
  color: var(--color-text-muted, #6b7280);
  margin: 0;
}
.structure__state {
  color: var(--color-text-muted, #6b7280);
}
.structure__state--error,
.structure__state--empty {
  padding: 1rem 0;
}
.structure__layout {
  display: grid;
  grid-template-columns: minmax(16rem, 1fr) 2fr;
  gap: 1.5rem;
  align-items: start;
}
@media (max-width: 40rem) {
  .structure__layout {
    grid-template-columns: 1fr;
  }
}
.structure__tree {
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  padding: 0.5rem;
  max-height: 70vh;
  overflow-y: auto;
}
.volume__toggle {
  display: flex;
  gap: 0.5rem;
  width: 100%;
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  text-align: left;
  font-size: 1rem;
}
.volume__marker {
  width: 1rem;
  text-align: center;
}
.volume__title {
  font-weight: 600;
}
.pian {
  list-style: none;
  margin: 0;
  padding: 0 0 0 1.5rem;
}
.pian__title {
  font-weight: 500;
  padding: 0.375rem 0;
}
.duan {
  list-style: none;
  margin: 0;
  padding: 0 0 0.5rem 0;
}
.duan__link {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  color: var(--color-text, #111827);
  font-size: 0.875rem;
  line-height: 1.4;
}
.duan__link--active {
  background: var(--color-primary-soft, #eef2ff);
}
.passage__text {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--color-primary, #4f46e5);
  background: var(--color-bg-soft, #f9fafb);
  font-size: 1.0625rem;
  line-height: 1.8;
}
.citation {
  margin: 0 0 1rem;
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
}
.citation__label {
  color: var(--color-text-muted, #6b7280);
  font-size: 0.875rem;
}
.citation__value {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 0.875rem;
}
.annotations__heading {
  font-size: 1rem;
  margin: 1rem 0 0.5rem;
}
.annotations__list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.annotations__item {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}
.annotations__note {
  margin: 0;
}
.annotations__remove {
  background: none;
  border: none;
  color: var(--color-danger, #dc2626);
  cursor: pointer;
}
.annotations__empty {
  color: var(--color-text-muted, #6b7280);
  padding: 0.5rem 0;
}
.annotations__form {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.5rem;
}
.annotations__label {
  font-size: 0.875rem;
  color: var(--color-text-muted, #6b7280);
}
.annotations__input {
  width: 100%;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.375rem;
  padding: 0.5rem;
  font: inherit;
}
.annotations__submit {
  justify-self: start;
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  background: var(--color-primary, #4f46e5);
  color: #fff;
  cursor: pointer;
}
.annotations__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.annotations__error {
  color: var(--color-danger, #dc2626);
  font-size: 0.875rem;
}
</style>
