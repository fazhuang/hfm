<script setup lang="ts">
import { ref } from 'vue'
import { ApiError } from '../../services/api'
import { resolveLocator, searchPublished } from '../../services/reader'
import type { PassageLocator, ReaderPassage, SearchResultItem } from '../../types/reader'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'ReaderView' })

const locatorInput = ref('work-1/edition-1/version-1/passage-1')
const passages = ref<ReaderPassage[]>([])
const resolved = ref<ReaderPassage | null>(null)
const readerError = ref<string | null>(null)
const query = ref('')
const results = ref<SearchResultItem[]>([])
const searching = ref(false)

function parseLocator(input: string): PassageLocator | undefined {
  const parts = input.split('/')
  if (parts.length < 3) return undefined
  return {
    workId: parts[0],
    editionId: parts[1],
    versionId: parts[2],
    passageId: parts[3],
  }
}

function onResolve(): void {
  readerError.value = null
  const locator = parseLocator(locatorInput.value)
  if (!locator) {
    readerError.value = '无效定位符（需 work/edition/version/passage）。'
    return
  }
  resolved.value = resolveLocator(locator, passages.value) ?? null
  if (!resolved.value) {
    readerError.value = '定位符未解析到已发布内容。'
  }
}

async function onSearch(): Promise<void> {
  searching.value = true
  try {
    results.value = await searchPublished(query.value)
  } catch (err) {
    readerError.value = err instanceof ApiError ? err.message : '搜索失败。'
  } finally {
    searching.value = false
  }
}
</script>

<template>
  <section aria-labelledby="reader-heading">
    <h1 id="reader-heading">原文阅读</h1>

    <form class="reader-form" @submit.prevent="onResolve">
      <label for="locator-input">定位符</label>
      <input id="locator-input" v-model="locatorInput" type="text" />
      <button type="submit">解析</button>
    </form>
    <ErrorState v-if="readerError" :message="readerError" />

    <article v-if="resolved" class="passage" aria-label="passage">
      <blockquote>{{ resolved.quotation }}</blockquote>
      <p class="passage__meta">{{ resolved.sourceTitle }} · {{ resolved.citation }}</p>
      <p class="passage__rights">{{ resolved.rightsNote }}</p>
    </article>
    <EmptyState v-else-if="!readerError" label="输入定位符以打开原文。" />

    <hr />

    <form class="search-form" @submit.prevent="onSearch">
      <label for="search-input">检索</label>
      <input id="search-input" v-model="query" type="search" />
      <button type="submit" :disabled="searching">搜索</button>
    </form>
    <LoadingState v-if="searching" />
    <ul v-else class="search-results">
      <li v-for="item in results" :key="item.id" class="search-results__item">
        <strong>{{ item.title }}</strong>
        <span>{{ item.sourceContext }}</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.reader-form,
.search-form {
  display: flex;
  gap: var(--hfm-space-2);
  align-items: center;
  margin-bottom: var(--hfm-space-4);
}

.passage {
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  padding: var(--hfm-space-4);
  background: var(--hfm-color-surface);
}

.passage__meta,
.passage__rights {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.search-results {
  list-style: none;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.search-results__item {
  display: grid;
  gap: var(--hfm-space-1);
}
</style>
