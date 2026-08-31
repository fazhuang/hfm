<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ApiError, fetchPublicMedia, fetchPublicPerson } from '../../services/api'
import {
  formatBytes,
  isPlayableVideo,
  MEDIA_CATEGORY_LABELS,
  mediaBytesUrl,
} from '../../services/media'
import type { MediaAssetItem } from '../../types/media'
import type { PublicPerson } from '../../types/public'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'PersonDetailView' })

const route = useRoute()
const person = ref<PublicPerson | null>(null)
const movies = ref<MediaAssetItem[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  const entityId = String(route.params.id ?? '')
  try {
    person.value = await fetchPublicPerson(entityId)
    const media = await fetchPublicMedia('movie')
    movies.value = media.slice(0, 8)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '人物资料加载失败。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section aria-labelledby="person-heading">
    <p><a class="back-link" href="/">← 返回首页</a></p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="person === null" label="人物不存在或未发布。" />

    <template v-else>
      <h1 id="person-heading">{{ person.name_zh || '未命名' }}</h1>
      <p class="person-meta">
        {{ person.name_pinyin || '' }}
        <template v-if="person.courtesy_name"> · 字 {{ person.courtesy_name }}</template>
        <template v-if="person.pseudonym"> · 号 {{ person.pseudonym }}</template>
        <template v-if="person.dynasty"> · {{ person.dynasty }}</template>
      </p>

      <h2 class="section-title">影视资料</h2>
      <EmptyState v-if="movies.length === 0" label="暂无影视资料。" />
      <ul v-else class="movie-list">
        <li v-for="movie in movies" :key="movie.id" class="movie-card">
          <h3 class="movie-card__title">{{ movie.name }}</h3>
          <p class="movie-card__meta">
            {{ MEDIA_CATEGORY_LABELS[movie.category] }} · {{ formatBytes(movie.byte_size) }}
          </p>
          <p class="movie-card__rights">{{ movie.license_basis }}</p>
          <video
            v-if="isPlayableVideo(movie.mime_type)"
            :src="mediaBytesUrl(movie.id)"
            controls
            preload="none"
          />
          <p v-else>
            <a class="open-link" :href="mediaBytesUrl(movie.id)" target="_blank" rel="noopener"
              >打开</a
            >
          </p>
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

.person-meta {
  color: var(--hfm-color-text-muted);
}

.section-title {
  margin: var(--hfm-space-5) 0 var(--hfm-space-3);
}

.movie-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-4);
}

.movie-card {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.movie-card__title {
  margin: 0 0 var(--hfm-space-1);
}

.movie-card__meta {
  margin: 0 0 var(--hfm-space-1);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.movie-card__rights {
  margin: 0 0 var(--hfm-space-2);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-xs);
}

.movie-card video {
  width: 100%;
  max-height: 420px;
  background: var(--hfm-color-bg);
  border-radius: var(--hfm-radius-sm);
}

.open-link {
  color: var(--hfm-color-accent);
  text-decoration: none;
  font-weight: 600;
}
</style>
