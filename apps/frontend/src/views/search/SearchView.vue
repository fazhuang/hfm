<script setup lang="ts">
import { ref } from 'vue'
import { ApiError, searchPublicHits } from '../../services/api'
import { mediaBytesUrl } from '../../services/media'
import type { SearchHit } from '../../types/public'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'SearchView' })

const query = ref('')
const results = ref<SearchHit[]>([])
const error = ref<string | null>(null)
const loading = ref(false)
const searched = ref(false)

const KIND_LABELS: Record<string, string> = {
  passage: '文献片段',
  work: '著作',
  person: '人物',
  c_term: '词条',
  heritage_project: '传承谱系',
  edition: '版本',
  media: '资料',
}

async function runSearch(): Promise<void> {
  const q = query.value.trim()
  if (!q) return
  loading.value = true
  error.value = null
  try {
    results.value = await searchPublicHits(q)
    searched.value = true
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '搜索失败。'
  } finally {
    loading.value = false
  }
}

function hitHref(hit: SearchHit): string | null {
  if (hit.kind === 'work') return `/works/${hit.id}`
  if (hit.kind === 'person') return `/persons/${hit.id}`
  if (hit.kind === 'media') return mediaBytesUrl(hit.id)
  return null
}
</script>

<template>
  <section aria-labelledby="search-heading">
    <h1 id="search-heading">检索</h1>
    <p class="search-intro">检索已发布的著作、人物、版本与资料（公开投影）。</p>

    <form class="search-form" @submit.prevent="runSearch">
      <label for="search-query" class="visually-hidden">关键词</label>
      <input
        id="search-query"
        v-model="query"
        type="search"
        placeholder="例如：五车楼 / 皇甫谧 / 四库全书"
      />
      <button type="submit" :disabled="loading">搜索</button>
    </form>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="searched && results.length === 0" label="未找到匹配的已发布内容。" />

    <ul v-else class="search-list">
      <li v-for="hit in results" :key="`${hit.kind}-${hit.id}`" class="search-item">
        <a v-if="hitHref(hit)" :href="hitHref(hit)!" class="search-item__main">
          <span class="search-item__kind">{{ KIND_LABELS[hit.kind] || hit.kind }}</span>
          <span class="search-item__title">{{ hit.title }}</span>
        </a>
        <template v-else>
          <span class="search-item__kind">{{ KIND_LABELS[hit.kind] || hit.kind }}</span>
          <span class="search-item__title">{{ hit.title }}</span>
        </template>
        <span v-if="hit.snippet" class="search-item__snippet">{{ hit.snippet }}</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.search-intro {
  color: var(--hfm-color-text-muted);
}

.search-form {
  display: flex;
  gap: var(--hfm-space-2);
  align-items: center;
  margin-bottom: var(--hfm-space-4);
}

.search-form input {
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  flex: 1;
  min-width: 220px;
}

.search-form button {
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
}

.search-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.search-item {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.search-item__main {
  display: flex;
  gap: var(--hfm-space-2);
  align-items: baseline;
  color: var(--hfm-color-text);
  text-decoration: none;
}

.search-item__kind {
  font-size: var(--hfm-text-xs);
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-bg);
  color: var(--hfm-color-text-muted);
  white-space: nowrap;
}

.search-item__title {
  font-weight: 600;
  overflow-wrap: anywhere;
}

.search-item__snippet {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
</style>
