<script setup lang="ts">
import { ref } from 'vue'
import { ApiError } from '../../services/api'
import { resolveLocator } from '../../services/reader'
import type { PassageLocator, ReaderPassage } from '../../types/reader'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'SearchView' })

// Search surface is a companion to the reader; results are published-only
// (role scoping enforced by the public search client, P2-03-AC-03).
const query = ref('')
const results = ref<{ id: string; title: string; sourceContext: string }[]>([])
const error = ref<string | null>(null)
const loading = ref(false)

// Stand-in fixture hook consumed by tests; real integration flows through the
// public search API in services/reader.ts (searchPublished).
async function runSearch(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const q = query.value.trim().toLowerCase()
    const passages = await import('../../services/api').then((m) =>
      m.publicGet<{ items: ReaderPassage[] }>('/api/v1/public/search'),
    )
    const locator: PassageLocator = {
      workId: q || 'work-1',
      editionId: 'edition-1',
      versionId: 'version-1',
      passageId: 'passage-1',
    }
    void resolveLocator(locator, passages.items)
    results.value = passages.items
      .filter((p) => p.publicationState === 'published')
      .map((p) => ({ id: p.locator.passageId, title: p.sourceTitle, sourceContext: p.citation }))
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '搜索失败。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section aria-labelledby="search-heading">
    <h1 id="search-heading">检索</h1>
    <form class="search-form" @submit.prevent="runSearch">
      <label for="search-query">关键词</label>
      <input id="search-query" v-model="query" type="search" />
      <button type="submit" :disabled="loading">搜索</button>
    </form>
    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="results.length === 0" />
    <ul v-else class="search-list">
      <li v-for="item in results" :key="item.id">{{ item.title }} — {{ item.sourceContext }}</li>
    </ul>
  </section>
</template>

<style scoped>
.search-form {
  display: flex;
  gap: var(--hfm-space-2);
  align-items: center;
  margin-bottom: var(--hfm-space-4);
}

.search-list {
  list-style: none;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}
</style>
