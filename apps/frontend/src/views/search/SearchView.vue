<script setup lang="ts">
/**
 * SearchView — UI-10 entity-aware scholarly discovery.
 *
 * Local deterministic index over the established content semantics
 * (person / text / work / edition / archive / paper). URL is the single
 * source of truth (?q= &type= &page=): refresh + back/forward recover state.
 * Facet counts come from the current result set; audited paper total (515)
 * is shown separately from searchable structured records (5).
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { SearchType } from '../../types/search'
import {
  AUDITED_PAPER_TOTAL,
  PAGE_SIZE,
  SEARCHABLE_PAPER_TOTAL,
  facetCounts,
  searchIndex,
  searchTypeLabel,
} from '../../data/searchIndex'
import { parseSearchQuery, serializeSearchQuery } from '../../composables/useSearchQuery'
import SearchHighlight from '../../components/search/SearchHighlight.vue'
import BibliographyEntry from '../../components/search/BibliographyEntry.vue'

defineOptions({ name: 'SearchView' })

const route = useRoute()
const router = useRouter()

// Local input bound to the form; synced from/into the URL.
const inputValue = ref('')

const state = computed(() => parseSearchQuery(route?.query ?? {}))
const q = computed(() => state.value.q)
const type = computed<SearchType | 'all'>(() => state.value.type)
const page = computed(() => state.value.page)

// Keep the input in sync when the URL changes externally (back/forward).
watch(q, (value) => {
  inputValue.value = value
})
watch(
  () => route?.query,
  () => {
    inputValue.value = q.value
  },
)

function syncInput(): void {
  inputValue.value = q.value
}
syncInput()

/** Results matching q (before type filter) — used for facet counts. */
const qResults = computed(() => searchIndex(q.value, 'all'))

/** Results after type filter — the actual result set. */
const filteredResults = computed(() => searchIndex(q.value, type.value))

const facets = computed(() => facetCounts(qResults.value))

const totalPages = computed(() => Math.max(1, Math.ceil(filteredResults.value.length / PAGE_SIZE)))

const currentPage = computed(() => Math.min(page.value, totalPages.value))

const pagedResults = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredResults.value.slice(start, start + PAGE_SIZE)
})

function updateQuery(patch: Record<string, string>): void {
  const next = { ...serializeSearchQuery(state.value), ...patch }
  void router?.replace({ query: next })
}

function onSubmit(): void {
  updateQuery({ q: inputValue.value.trim(), type: 'all', page: '1' })
}

function onSelectType(next: SearchType | 'all'): void {
  updateQuery({ type: next === 'all' ? '' : next, page: '1' })
}

function onClear(): void {
  inputValue.value = ''
  void router?.replace({ query: {} })
}

function goToPage(p: number): void {
  if (p < 1 || p > totalPages.value) return
  updateQuery({ page: p > 1 ? String(p) : '' })
}

const hasQuery = computed(() => q.value.length > 0)

/** Deterministic suggestion entries for the empty/initial states. */
const SUGGESTIONS = [
  { label: '皇甫谧', href: '/persons/person-huangfu-mi' },
  { label: '《针灸甲乙经》', href: '/jiayi' },
  { label: '《帝王世纪》', href: '/works' },
  { label: '《高士传》', href: '/works' },
  { label: '黄龙祥（校注本）', href: '/jiayi#scholarship' },
  { label: '非遗传承', href: '/heritage' },
] as const
</script>

<template>
  <section class="search" aria-labelledby="search-heading">
    <header class="search-hero">
      <p class="hfm-eyebrow">数字人文 · 学术检索</p>
      <h1 id="search-heading" class="search-hero__title">检索</h1>

      <form class="search-form" role="search" @submit.prevent="onSubmit">
        <label class="visually-hidden" for="search-input">检索平台内容</label>
        <input
          id="search-input"
          v-model="inputValue"
          type="search"
          placeholder="检索人物、作品、版本、档案、论文… 例如：皇甫谧 / 甲乙经 / 黄龙祥"
        />
        <button type="submit" class="search-form__submit">检索</button>
      </form>
    </header>

    <!-- Initial state: no query -->
    <template v-if="!hasQuery">
      <section class="search-section" aria-labelledby="overview-heading">
        <h2 id="overview-heading" class="section-title">可检索内容</h2>
        <ul class="type-overview">
          <li v-for="facet in facets" :key="facet.type" class="type-overview__item">
            <span class="type-overview__label">{{ facet.label }}</span>
            <span class="type-overview__count">{{ facet.count }}</span>
          </li>
        </ul>
        <p class="search-note">
          客户资料收录论文 {{ AUDITED_PAPER_TOTAL }} 篇；当前已结构化题录
          {{ SEARCHABLE_PAPER_TOTAL }} 条（题录整理持续进行）。
        </p>
      </section>

      <section class="search-section" aria-labelledby="entries-heading">
        <h2 id="entries-heading" class="section-title">内容入口</h2>
        <ul class="entry-list">
          <li v-for="s in SUGGESTIONS" :key="s.label" class="entry-item">
            <a :href="s.href" class="entry-item__link">{{ s.label }}</a>
          </li>
        </ul>
      </section>
    </template>

    <!-- Query state -->
    <template v-else>
      <p class="search-summary" role="status" aria-live="polite">
        找到 {{ filteredResults.length }} 条结果
        <template v-if="type !== 'all'">（{{ searchTypeLabel(type) }}）</template>
        <template
          v-if="SEARCHABLE_PAPER_TOTAL > 0 && AUDITED_PAPER_TOTAL !== SEARCHABLE_PAPER_TOTAL"
        >
          · 论文题录：已结构化 {{ SEARCHABLE_PAPER_TOTAL }} / 审计 {{ AUDITED_PAPER_TOTAL }}
        </template>
      </p>

      <div class="search-layout">
        <aside class="facet-panel" aria-label="筛选">
          <h2 class="facet-title">内容类型</h2>
          <ul class="facet-list">
            <li>
              <button
                type="button"
                class="facet-btn"
                :class="{ 'facet-btn--active': type === 'all' }"
                :aria-pressed="type === 'all'"
                @click="onSelectType('all')"
              >
                <span class="facet-btn__label">全部</span>
                <span class="facet-btn__count">{{ qResults.length }}</span>
              </button>
            </li>
            <li v-for="facet in facets" :key="facet.type">
              <button
                type="button"
                class="facet-btn"
                :class="{ 'facet-btn--active': type === facet.type }"
                :aria-pressed="type === facet.type"
                @click="onSelectType(facet.type)"
              >
                <span class="facet-btn__label">{{ facet.label }}</span>
                <span class="facet-btn__count">{{ facet.count }}</span>
              </button>
            </li>
          </ul>
        </aside>

        <div class="search-results">
          <p v-if="type !== 'all'" class="active-filter" aria-live="polite">
            当前筛选：{{ searchTypeLabel(type) }}
            <button type="button" class="active-filter__clear" @click="onSelectType('all')">
              清除筛选
            </button>
          </p>

          <!-- Empty state -->
          <div v-if="pagedResults.length === 0" class="empty-state" role="status">
            <p class="empty-state__title">未找到匹配「{{ q }}」的结果</p>
            <p class="empty-state__hint">
              可尝试：作品名（针灸甲乙经）、人物名（皇甫谧）、整理者（黄龙祥）。
            </p>
            <button type="button" class="empty-state__clear" @click="onClear">
              清除关键词，查看全部内容
            </button>
          </div>

          <!-- Results -->
          <ol v-else class="result-list">
            <template v-for="result in pagedResults" :key="result.entry.id">
              <!-- PAPER → BibliographyEntry -->
              <BibliographyEntry
                v-if="result.entry.type === 'paper'"
                :entry="result.entry"
                :query="q"
              />
              <!-- others → generic scholarly row -->
              <li v-else class="result-row">
                <p class="result-row__type">{{ searchTypeLabel(result.entry.type) }}</p>
                <p class="result-row__title">
                  <a v-if="result.entry.route" :href="result.entry.route" class="result-row__link">
                    <SearchHighlight :text="result.entry.title" :query="q" />
                  </a>
                  <template v-else
                    ><SearchHighlight :text="result.entry.title" :query="q"
                  /></template>
                </p>
                <p v-if="result.entry.subtitle" class="result-row__meta">
                  <SearchHighlight :text="result.entry.subtitle" :query="q" />
                </p>
                <p
                  v-if="result.entry.authors && result.entry.authors.length"
                  class="result-row__authors"
                >
                  {{ result.entry.authors.join('；') }}
                </p>
                <p v-if="result.entry.sourceName" class="result-row__source">
                  {{ result.entry.sourceName }}
                </p>
              </li>
            </template>
          </ol>

          <!-- Pagination -->
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
        </div>
      </div>
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

.type-overview {
  list-style: none;
  margin: 0 0 var(--hfm-space-3);
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(9rem, 1fr));
  gap: var(--hfm-space-2);
}

.type-overview__item {
  display: flex;
  justify-content: space-between;
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  font-size: var(--hfm-text-sm);
}

.type-overview__count {
  color: var(--hfm-color-heritage);
  font-variant-numeric: tabular-nums;
}

.search-note {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
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

.search-layout {
  display: grid;
  grid-template-columns: 13rem 1fr;
  gap: var(--hfm-space-6);
  align-items: start;
}

.facet-panel {
  position: sticky;
  top: var(--hfm-space-4);
}

.facet-title {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
  margin: 0 0 var(--hfm-space-2);
}

.facet-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.facet-btn {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: var(--hfm-space-2);
  padding: var(--hfm-space-1) var(--hfm-space-2);
  border: none;
  border-left: 3px solid transparent;
  background: none;
  color: var(--hfm-color-text-secondary);
  cursor: pointer;
  font-size: var(--hfm-text-sm);
  text-align: left;
}

.facet-btn:hover {
  color: var(--hfm-color-text);
  background: var(--hfm-color-canvas);
}

.facet-btn--active {
  border-left-color: var(--hfm-color-accent);
  color: var(--hfm-color-accent);
  font-weight: 600;
}

.facet-btn__count {
  font-variant-numeric: tabular-nums;
  color: var(--hfm-color-text-muted);
}

.active-filter {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-3);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  margin: 0 0 var(--hfm-space-3);
}

.active-filter__clear {
  border: none;
  background: none;
  color: var(--hfm-color-interactive);
  cursor: pointer;
  padding: 0;
  font-size: var(--hfm-text-sm);
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
}

.result-row__link {
  color: var(--hfm-color-text);
  text-decoration: none;
}

.result-row__link:hover {
  color: var(--hfm-color-accent);
}

.result-row__meta,
.result-row__authors,
.result-row__source {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
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

@media (max-width: 767px) {
  .search-layout {
    grid-template-columns: 1fr;
  }

  .facet-panel {
    position: static;
  }

  .facet-list {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--hfm-space-2);
  }

  .facet-btn {
    border: 1px solid var(--hfm-color-border);
    border-left-width: 3px;
    border-radius: var(--hfm-radius-sm);
    padding: var(--hfm-space-2);
  }
}
</style>
