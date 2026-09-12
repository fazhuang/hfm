<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ApiError, fetchPublicWorks, publicGet } from '../../services/api'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'ReaderView' })

interface PassageNode {
  passage_id: string
  order: number
  version_id: string | null
  preview: string
}
interface ChapterNode {
  chapter_id: string
  title: string
  order: number | null
  passages: PassageNode[]
}

const loading = ref(true)
const error = ref<string | null>(null)
const workTitle = ref('')
const chapters = ref<ChapterNode[]>([])
const activeChapter = ref<ChapterNode | null>(null)
const activePassage = ref<PassageNode | null>(null)
const passageText = ref('')
const passageLocator = ref('')
const reading = ref(false)

onMounted(async () => {
  try {
    const works = await fetchPublicWorks()
    const jiayi = works.works.find((w) => w.title === '针灸甲乙经')
    if (!jiayi) {
      error.value = '未找到可阅读的已发布著作。'
      return
    }
    const structure = await publicGet<{ title: string; chapters: ChapterNode[] }>(
      `/api/v1/public/works/${jiayi.work_id}/structure`,
    )
    workTitle.value = structure.title
    chapters.value = structure.chapters
    if (chapters.value.length > 0) {
      activeChapter.value = chapters.value[0]
      if (chapters.value[0].passages.length > 0) {
        await openPassage(chapters.value[0].passages[0])
      }
    }
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '阅读器加载失败。'
  } finally {
    loading.value = false
  }
})

async function openPassage(passage: PassageNode): Promise<void> {
  activePassage.value = passage
  reading.value = true
  try {
    const data = await publicGet<{ quotation?: string; locator?: string }>(
      `/api/v1/public/reader/resolve?passage_id=${passage.passage_id}`,
    )
    passageText.value = (data.quotation ?? '').replace(/\n{2,}/g, '\n').trim()
    passageLocator.value = data.locator ?? ''
  } catch (err) {
    passageText.value = ''
    passageLocator.value = ''
    if (err instanceof ApiError && err.status === 404) {
      // 该段落未发布或已撤回：保持空，阅读器 fail-closed
      passageText.value = ''
    }
  } finally {
    reading.value = false
  }
}

function selectChapter(chapter: ChapterNode): void {
  activeChapter.value = chapter
  if (chapter.passages.length > 0) {
    void openPassage(chapter.passages[0])
  }
}
</script>

<template>
  <section aria-labelledby="reader-heading">
    <h1 id="reader-heading">阅读</h1>
    <p class="reader-intro">
      当前阅读：《{{ workTitle }}》· OCR
      演示正文（现代解读本《针灸甲乙经一学就通》，未人工校对，仅用于演示）。
    </p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="chapters.length === 0" label="暂无已发布正文。" />

    <div v-else class="reader-layout">
      <nav class="toc" aria-label="章节目录">
        <button
          v-for="chapter in chapters"
          :key="chapter.chapter_id"
          type="button"
          :class="[
            'toc__item',
            { 'toc__item--active': activeChapter?.chapter_id === chapter.chapter_id },
          ]"
          @click="selectChapter(chapter)"
        >
          {{ chapter.title }}（{{ chapter.passages.length }} 段）
        </button>
      </nav>

      <article class="text-panel" aria-live="polite">
        <template v-if="activeChapter">
          <h2 class="text-panel__chapter">{{ activeChapter.title }}</h2>
          <div class="text-panel__pager">
            <button
              type="button"
              :disabled="!activePassage || activePassage.order <= activeChapter.passages[0]?.order"
              @click="
                activePassage &&
                openPassage(
                  activeChapter.passages[
                    Math.max(
                      0,
                      activeChapter.passages.findIndex(
                        (p) => p.passage_id === activePassage!.passage_id,
                      ) - 1,
                    )
                  ],
                )
              "
            >
              上一段
            </button>
            <span>{{ activePassage ? `第 ${activePassage.order} 页` : '—' }}</span>
            <button
              type="button"
              :disabled="
                !activePassage ||
                activePassage.order >=
                  activeChapter.passages[activeChapter.passages.length - 1]?.order
              "
              @click="
                activePassage &&
                openPassage(
                  activeChapter.passages[
                    Math.min(
                      activeChapter.passages.length - 1,
                      activeChapter.passages.findIndex(
                        (p) => p.passage_id === activePassage!.passage_id,
                      ) + 1,
                    )
                  ],
                )
              "
            >
              下一段
            </button>
          </div>
          <LoadingState v-if="reading" />
          <p v-else-if="passageText" class="text-panel__body">{{ passageText }}</p>
          <EmptyState v-else label="该段落不可用（未发布或已撤回）。" />
          <p v-if="passageLocator" class="text-panel__locator">定位符：{{ passageLocator }}</p>
        </template>
      </article>
    </div>
  </section>
</template>

<style scoped>
.reader-intro {
  color: var(--hfm-color-text-muted);
}

.reader-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--hfm-space-4);
  align-items: start;
}

@media (max-width: 767px) {
  .reader-layout {
    grid-template-columns: 1fr;
  }
}

.toc {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-2);
}

.toc__item {
  text-align: left;
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  cursor: pointer;
}

.toc__item--active {
  border-color: var(--hfm-color-accent);
  color: var(--hfm-color-accent);
  font-weight: 600;
}

.text-panel {
  padding: var(--hfm-space-5);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-lg);
  background: var(--hfm-color-surface);
}

.text-panel__chapter {
  margin: 0 0 var(--hfm-space-3);
}

.text-panel__pager {
  display: flex;
  gap: var(--hfm-space-3);
  align-items: center;
  margin-bottom: var(--hfm-space-4);
}

.text-panel__pager button {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  cursor: pointer;
}

.text-panel__pager button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-panel__body {
  white-space: pre-wrap;
  line-height: 1.9;
  font-size: var(--hfm-text-base);
}

.text-panel__locator {
  margin-top: var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  overflow-wrap: anywhere;
}
</style>
