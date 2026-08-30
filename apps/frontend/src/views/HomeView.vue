<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ApiError, fetchPublicHome } from '../services/api'
import EmptyState from '../components/states/EmptyState.vue'
import ErrorState from '../components/states/ErrorState.vue'
import LoadingState from '../components/states/LoadingState.vue'
import type { PublishedItem } from '../types/public'
import { publishedOnly } from '../utils/publication'

const loading = ref(true)
const error = ref<string | null>(null)
const items = ref<PublishedItem[]>([])

onMounted(async () => {
  try {
    const projection = await fetchPublicHome()
    items.value = publishedOnly(projection.items)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Unable to load public content.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section aria-labelledby="portal-heading">
    <h1 id="portal-heading">皇甫谧人文数字平台 · 公开门户</h1>
    <p>公开门户只展示已获准发布的内容；未发布或已撤回内容不会出现在这里。</p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="items.length === 0" />
    <ul v-else class="portal-list">
      <li v-for="item in items" :key="item.id" class="portal-list__item">
        {{ item.title }}
      </li>
    </ul>
  </section>
</template>

<style scoped>
.portal-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.portal-list__item {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}
</style>
