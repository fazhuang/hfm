<script setup lang="ts">
/**
 * SearchView — CF-06 scholarly discovery on the real public search API.
 *
 * QUERY → frontend API client (searchPublicHits) → GET /api/v1/public/search
 *   → FastAPI → PostgreSQL → JSON → typed projection → presentation.
 *
 * The local static searchIndex is NOT the runtime result source for the
 * public surface (P1-SEARCH-02 closed); it remains only on the
 * authenticated research surface. Static content here is limited to
 * non-result presentation data: entry-point links and scope copy.
 *
 * URL is the single source of truth for q (and page): refresh and
 * back/forward recover state. States are discriminated (CF-06 §7):
 *   idle → no query; loading → in flight; ready → results; empty → 0 total
 *   (never an error); error → API/network failure (never shown as 暂无结果).
 * HTTP 4xx (bad request) and 5xx/network are rendered distinctly.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError, searchPublicHits } from '../../services/api'
import { toSearchResultRows, type SearchResultRow } from '../../presentation/searchResults'
import SearchHighlight from '../../components/search/SearchHighlight.vue'

defineOptions({ name: 'SearchView' })

type PageStatus = 'idle' | 'loading' | 'ready' | 'empty' | 'error'

const PAGE_SIZE = 20

const route = useRoute()
const router = useRouter()

const inputValue = ref('')
const status = ref<PageStatus>('idle')
const rows = ref<SearchResultRow[]>([])
const total = ref(0)
const currentPage = ref(1)
const errorMessage = ref('')
const errorKind = ref<'client' | 'server' | 'network'>('server')

const q = computed(() => (typeof route.query.q === 'string' ? route.query.q.trim() : ''))
const pageParam = computed(() => {
  const raw = typeof route.query.page === 'string' ? Number.parseInt(route.query.page, 10) : NaN
  return Number.isFinite(raw) && raw > 0 ? raw : 1
})

watch(
  q,
  (value) => {
    inputValue.value = value
  },
  { immediate: true },
)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

async function runSearch(query: string, page: number): Promise<void> {
  status.value = 'loading'
  errorMessage.value = ''
  try {
    const result = await searchPublicHits(query, page, PAGE_SIZE)
    if (q.value !== query || currentPage.value !== page) return // stale response
    total.value = result.total
    rows.value = toSearchResultRows(result.hits)
    currentPage.value = page
    status.value = result.total === 0 ? 'empty' : 'ready'
  } catch (err) {
    if (q.value !== query || currentPage.value !== page) return
    if (err instanceof ApiError && err.status >= 400 && err.status < 500) {
      errorKind.value = 'client'
      errorMessage.value = '检索条件无效，请调整后重试。'
    } else {
      errorKind.value = err instanceof ApiError ? 'server' : 'network'
      errorMessage.value = '检索服务暂时不可用，请稍后重试。'
    }
    status.value = 'error'
  }
}

function updateQuery(next: Record<string, string>): void {
  void router?.replace({ query: next })
}

function onSubmit(): void {
  const query = inputValue.value.trim()
  if (query === '') {
    void router?.replace({ query: {} })
    return
  }
  updateQuery({ q: query })
}

function clearAndSearch(): void {
  inputValue.value = ''
  void router?.replace({ query: {} })
}

function goToPage(p: number): void {
  if (p < 1 || p > totalPages.value) return
  const next: Record<string, string> = { q: q.value }
  if (p > 1) next.page = String(p)
  updateQuery(next)
}

watch(
  () => [q.value, pageParam.value] as const,
  ([query, page]) => {
    currentPage.value = page
    if (query === '') {
      status.value = 'idle'
      rows.value = []
      total.value = 0
      return
    }
    void runSearch(query, page)
  },
  { immediate: true },
)

/** Static content entry points (non-result presentation data). */
const SUGGESTIONS = [
  { label: '皇甫谧', href: '/persons/ENT-PERSON-HFM-HUANGFUMI' },
  { label: '《针灸甲乙经》', href: '/jiayi' },
  { label: '非遗传承', href: '/heritage' },
  { label: '人物档案', href: '/persons/ENT-PERSON-HFM-HUANGFUMI' },
] as const

const SCOPE_KINDS = ['人物', '作品', '版本', '非遗档案', '术语', '文本片段'] as const
</script>

<template>
  <section class="search" aria-labelledby="search-heading">
    <header class="search-hero">
      <p class="hfm-eyebrow">数字人文 · 学术检索</p>
      <h1 id="search-heading" class="search-hero__title">检索</h1>

      <form class="search-form" role="search" aria-label="全文检索" @submit.prevent="onSubmit">
        <label class="visually-hidden" for="search-input">检索平台内容</label>
        <input
          id="search-input"
          v-model="inputValue"
          type="search"
          autocomplete="off"
          placeholder="检索已发布内容… 例如：皇甫谧 / 甲乙经"
        />
        <button type="submit" class="search-form__submit">检索</button>
      </form>
    </header>

    <!-- IDLE: no query — scope copy + static entry points only. -->
    <template v-if="status === 'idle'">
      <section class="search-section" aria-labelledby="overview-heading">
        <h2 id="overview-heading" class="section-title">检索范围</h2>
        <p class="search-note">
          检索覆盖平台已发布（PUBLISHED）的公开内容，按真实数据来源返回：{{
            SCOPE_KINDS.join('、')
          }}。结果均来自公开检索接口，随内容准入实时更新。
        </p>
      </section>

      <section class="search-section" aria-labelledby="entries-heading">
        <h2 id="entries-heading" class="section-title">内容入口</h2>
        <ul class="entry-list">
          <li v-for="s in SUGGESTIONS" :key="s.href + s.label" class="entry-item">
            <a :href="s.href" class="entry-item__link">{{ s.label }}</a>
          </li>
        </ul>
      </section>
    </template>

    <!-- QUERY STATES -->
    <template v-else>
      <!-- Live summary: updates only when the result set really changes. -->
      <p
        v-if="status === 'loading'"
        class="search-summary search-summary--live"
        role="status"
        aria-live="polite"
      >
        正在检索「{{ q }}」…
      </p>
      <p
        v-else-if="status === 'ready'"
        class="search-summary search-summary--live"
        role="status"
        aria-live="polite"
      >
        找到 {{ total }} 条结果
        <template v-if="total > 0">（第 {{ currentPage }} 页）</template>
      </p>

      <!-- ERROR: real failure — distinct from no-match, never masked as 暂无结果. -->
      <div v-if="status === 'error'" class="search-error" data-search-state="error" role="alert">
        <p class="search-error__title">{{ errorMessage }}</p>
        <p class="search-error__detail">
          {{
            errorKind === 'client'
              ? '请求未被接受（HTTP 4xx）。'
              : '服务未能完成检索（HTTP 5xx 或网络中断）。'
          }}
        </p>
        <button type="button" class="search-error__retry" @click="runSearch(q, currentPage)">
          重试
        </button>
      </div>

      <!-- EMPTY: 0 results is a valid outcome, not an error. -->
      <div
        v-else-if="status === 'empty'"
        class="empty-state"
        role="status"
        data-search-state="empty"
      >
        <p class="empty-state__title">未找到匹配「{{ q }}」的结果</p>
        <p class="empty-state__hint">可尝试：人物名（皇甫谧）、作品名（甲乙经）或项目名。</p>
        <button type="button" class="empty-state__clear" @click="clearAndSearch">清除关键词</button>
      </div>

      <!-- READY: real backend results. -->
      <template v-else-if="status === 'ready'">
        <ol class="result-list">
          <li v-for="row in rows" :key="`${row.kind}-${row.title}`" class="result-row">
            <p class="result-row__type">{{ row.kindLabel }}</p>
            <p class="result-row__title">
              <a v-if="row.href" :href="row.href" class="result-row__link">
                <SearchHighlight :text="row.title" :query="q" />
              </a>
              <template v-else><SearchHighlight :text="row.title" :query="q" /></template>
            </p>
            <p v-if="row.snippet !== ''" class="result-row__meta">
              <SearchHighlight :text="row.snippet" :query="q" />
            </p>
          </li>
        </ol>

        <nav v-if="totalPages > 1" class="pager" aria-label="结果分页">
          <button type="button" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
            上一页
          </button>
          <ol class="pager__pages">
            <li v-for="p in totalPages" :key="p">
              <button
                type="button"
                class="pager__page"
                :class="{ 'pager__page--current': p === currentPage }"
                :aria-current="p === currentPage ? 'page' : undefined"
                @click="goToPage(p)"
              >
                {{ p }}
              </button>
            </li>
          </ol>
          <button
            type="button"
            :disabled="currentPage >= totalPages"
            @click="goToPage(currentPage + 1)"
          >
            下一页
          </button>
        </nav>
      </template>
    </template>
  </section>
</template>

<style scoped>
.search {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.search-hero {
  padding: var(--hfm-space-6) 0 var(--hfm-space-5);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-8);
}

.search-hero__title {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-4);
  letter-spacing: var(--hfm-tracking-display);
}

.search-form {
  display: flex;
  gap: var(--hfm-space-2);
  max-width: 46rem;
}

.search-form input {
  flex: 1;
  min-width: 0;
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  font-size: var(--hfm-text-base);
}

.search-form__submit {
  padding: var(--hfm-space-2) var(--hfm-space-5);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
  font-weight: 600;
}

.search-section {
  margin-bottom: var(--hfm-space-10);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.search-note {
  color: var(--hfm-color-text-muted);
  max-width: 60ch;
  line-height: var(--hfm-leading-reading);
}

.entry-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.entry-item {
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.entry-item__link {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.entry-item__link:hover {
  text-decoration: underline;
}

.search-summary {
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
  margin: 0 0 var(--hfm-space-4);
}

.search-error {
  padding: var(--hfm-space-8) var(--hfm-space-4);
  text-align: center;
  border: 1px solid var(--hfm-color-danger);
  border-radius: var(--hfm-radius-md);
}

.search-error__title {
  font-weight: 600;
  margin: 0 0 var(--hfm-space-2);
  color: var(--hfm-color-danger);
}

.search-error__detail {
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
  margin: 0 0 var(--hfm-space-4);
}

.search-error__retry {
  padding: var(--hfm-space-1) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
}

.result-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.result-row {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.result-row__type {
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-azure);
  font-weight: 600;
}

.result-row__title {
  margin: 0;
  font-weight: 600;
  line-height: var(--hfm-leading-normal);
  overflow-wrap: anywhere;
}

.result-row__link {
  color: var(--hfm-color-text);
  text-decoration: none;
}

.result-row__link:hover {
  color: var(--hfm-color-accent);
}

.result-row__meta {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
  line-height: var(--hfm-leading-normal);
  overflow-wrap: anywhere;
}

.empty-state {
  padding: var(--hfm-space-10) var(--hfm-space-4);
  text-align: center;
  border: 1px dashed var(--hfm-color-border-strong);
  border-radius: var(--hfm-radius-md);
}

.empty-state__title {
  font-weight: 600;
  margin: 0 0 var(--hfm-space-2);
}

.empty-state__hint {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  margin: 0 0 var(--hfm-space-4);
}

.empty-state__clear {
  padding: var(--hfm-space-1) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
}

.pager {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  align-items: center;
  margin-top: var(--hfm-space-5);
}

.pager button {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
  cursor: pointer;
}

.pager button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pager__pages {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-1);
}

.pager__page--current {
  border-color: var(--hfm-color-accent) !important;
  color: var(--hfm-color-accent) !important;
  font-weight: 600;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
</style>
