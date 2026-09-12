<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ApiError, fetchPublicWork, fetchPublicWorkEditions } from '../../services/api'
import type { EditionSummary, WorkDetail } from '../../types/public'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'WorkDetailView' })

const route = useRoute()
const work = ref<WorkDetail | null>(null)
const editions = ref<EditionSummary[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  const workId = String(route.params.id ?? '')
  try {
    work.value = await fetchPublicWork(workId)
    const data = await fetchPublicWorkEditions(workId)
    editions.value = data.editions
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '作品资料加载失败。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section aria-labelledby="work-heading">
    <p><a class="back-link" href="/">← 返回首页</a></p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="work === null" label="作品不存在或未发布。" />

    <template v-else>
      <h1 id="work-heading">{{ work.title }}</h1>
      <p class="work-meta">
        <template v-if="work.dynasty">{{ work.dynasty }}</template>
        <template v-if="work.category"> · {{ work.category }}</template>
        <template v-if="work.edition_count !== undefined">
          · {{ work.edition_count }} 个版本</template
        >
      </p>
      <p>
        相关资料（论文 / 古籍 / 研究）请在
        <a class="open-link" href="/library">资料库</a> 中查阅。
      </p>

      <h2 class="section-title">版本列表</h2>
      <EmptyState v-if="editions.length === 0" label="暂无版本。" />
      <ul v-else class="edition-list">
        <li v-for="edition in editions" :key="edition.edition_id" class="edition-item">
          <span class="edition-item__name">{{ edition.edition_name }}</span>
          <span class="edition-item__meta">
            {{ edition.era || '年代不详' }}
            <template v-if="edition.publisher_block"> · {{ edition.publisher_block }}</template>
          </span>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.back-link {
  color: var(--hfm-color-accent);
  text-decoration: none;
}

.work-meta {
  color: var(--hfm-color-text-muted);
}

.open-link {
  color: var(--hfm-color-accent);
  text-decoration: none;
  font-weight: 600;
}

.section-title {
  margin: var(--hfm-space-5) 0 var(--hfm-space-3);
}

.edition-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.edition-item {
  display: flex;
  justify-content: space-between;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.edition-item__name {
  font-weight: 600;
  overflow-wrap: anywhere;
}

.edition-item__meta {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  white-space: nowrap;
}
</style>
