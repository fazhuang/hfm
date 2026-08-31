<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ApiError, fetchPublicMedia } from '../../services/api'
import {
  formatBytes,
  isPlayableVideo,
  MEDIA_CATEGORY_LABELS,
  mediaBytesUrl,
} from '../../services/media'
import type { MediaAssetItem, MediaCategory } from '../../types/media'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'MediaLibraryView' })

const PAGE_SIZE = 24
const all = ref<MediaAssetItem[]>([])
const active = ref<MediaCategory | 'all'>('all')
const keyword = ref('')
const page = ref(1)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    all.value = await fetchPublicMedia()
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '资料库加载失败。'
  } finally {
    loading.value = false
  }
})

const categories: Array<MediaCategory | 'all'> = ['all', 'paper', 'classic', 'movie']

const filtered = computed(() => {
  const kw = keyword.value.trim()
  return all.value.filter((m) => {
    if (active.value !== 'all' && m.category !== active.value) return false
    if (
      kw &&
      !m.name.toLowerCase().includes(kw.toLowerCase()) &&
      !m.object_key.toLowerCase().includes(kw.toLowerCase())
    )
      return false
    return true
  })
})

const paged = computed(() =>
  filtered.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE),
)
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PAGE_SIZE)))

function setCategory(cat: MediaCategory | 'all'): void {
  active.value = cat
  page.value = 1
}
</script>

<template>
  <section aria-labelledby="library-heading">
    <h1 id="library-heading">资料库</h1>
    <p class="library-intro">
      已发布资料共 {{ all.length }} 项。现代出版物与论文为第三方版权，平台以非商业非盈利方式
      仅供皇甫谧学术爱好者学习与宣传，请勿用于商业用途。
    </p>

    <div class="toolbar">
      <div class="tabs" role="tablist" aria-label="资料分类">
        <button
          v-for="cat in categories"
          :key="cat"
          type="button"
          :class="['tab', { 'tab--active': active === cat }]"
          :aria-selected="active === cat"
          @click="setCategory(cat)"
        >
          {{ cat === 'all' ? '全部' : MEDIA_CATEGORY_LABELS[cat] }}
        </button>
      </div>
      <label class="search">
        <span class="visually-hidden">搜索资料</span>
        <input v-model="keyword" type="search" placeholder="搜索资料名称…" />
      </label>
    </div>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="paged.length === 0" label="当前分类暂无资料。" />

    <ul v-else class="media-grid">
      <li v-for="asset in paged" :key="asset.id" class="media-card">
        <div class="media-card__head">
          <span class="media-card__badge">{{ MEDIA_CATEGORY_LABELS[asset.category] }}</span>
          <span class="media-card__size">{{ formatBytes(asset.byte_size) }}</span>
        </div>
        <h3 class="media-card__title">{{ asset.name }}</h3>
        <p class="media-card__rights">{{ asset.license_basis }}</p>
        <p v-if="asset.restriction" class="media-card__restriction">{{ asset.restriction }}</p>
        <div class="media-card__actions">
          <a
            v-if="isPlayableVideo(asset.mime_type)"
            :href="mediaBytesUrl(asset.id)"
            class="media-card__open"
            target="_blank"
            rel="noopener"
            >播放</a
          >
          <a
            v-else
            :href="mediaBytesUrl(asset.id)"
            class="media-card__open"
            target="_blank"
            rel="noopener"
            >打开 PDF</a
          >
        </div>
      </li>
    </ul>

    <nav v-if="totalPages > 1" class="pager" aria-label="分页">
      <button type="button" :disabled="page <= 1" @click="page -= 1">上一页</button>
      <span>第 {{ page }} / {{ totalPages }} 页</span>
      <button type="button" :disabled="page >= totalPages" @click="page += 1">下一页</button>
    </nav>
  </section>
</template>

<style scoped>
.library-intro {
  color: var(--hfm-color-text-muted);
  max-width: 70ch;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  align-items: center;
  margin: var(--hfm-space-4) 0;
}

.tabs {
  display: flex;
  gap: var(--hfm-space-2);
  flex-wrap: wrap;
}

.tab {
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  cursor: pointer;
}

.tab--active {
  border-color: var(--hfm-color-accent);
  color: var(--hfm-color-accent);
  font-weight: 600;
}

.search input {
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  min-width: 220px;
}

.media-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--hfm-space-3);
}

.media-card {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-2);
}

.media-card__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.media-card__badge {
  font-size: var(--hfm-text-xs);
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-bg);
  color: var(--hfm-color-text-muted);
}

.media-card__size {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.media-card__title {
  margin: 0;
  font-size: var(--hfm-text-base);
  overflow-wrap: anywhere;
}

.media-card__rights {
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  line-height: 1.5;
}

.media-card__restriction {
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-danger);
}

.media-card__actions {
  margin-top: auto;
}

.media-card__open {
  color: var(--hfm-color-accent);
  text-decoration: none;
  font-weight: 600;
}

.pager {
  display: flex;
  gap: var(--hfm-space-3);
  align-items: center;
  margin-top: var(--hfm-space-4);
}

.pager button {
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  cursor: pointer;
}

.pager button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
</style>
