<script setup lang="ts">
/**
 * ResearchSearchView — UI-11 research search (ONE INDEX, denser presentation).
 * Reuses the UI-10 SEARCH_INDEX + deterministic searchIndex — no second index.
 * Research presentation adds status/source/evidence/related metadata and a
 * Research view link per result.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  facetCounts,
  searchIndex,
  searchTypeLabel,
  AUDITED_PAPER_TOTAL,
  SEARCHABLE_PAPER_TOTAL,
} from '../../data/searchIndex'
import { parseSearchQuery, serializeSearchQuery } from '../../composables/useSearchQuery'
import type { SearchType } from '../../types/search'
import SearchHighlight from '../../components/search/SearchHighlight.vue'

defineOptions({ name: 'ResearchSearchView' })

const route = useRoute()
const router = useRouter()

const inputValue = ref('')
const state = computed(() => parseSearchQuery(route?.query ?? {}))
const q = computed(() => state.value.q)
const type = computed<SearchType | 'all'>(() => state.value.type)

watch(
  () => route?.query,
  () => {
    inputValue.value = q.value
  },
  { immediate: true },
)

const qResults = computed(() => searchIndex(q.value, 'all'))
const filteredResults = computed(() => searchIndex(q.value, type.value))
const facets = computed(() => facetCounts(qResults.value))

function updateQuery(patch: Record<string, string>): void {
  void router?.replace({ query: { ...serializeSearchQuery(state.value), ...patch } })
}

function onSubmit(): void {
  updateQuery({ q: inputValue.value.trim(), type: 'all', page: '1' })
}

function onSelectType(next: SearchType | 'all'): void {
  updateQuery({ type: next === 'all' ? '' : next, page: '1' })
}

function researchHref(entryType: string, id: string): string {
  // Reader docs and heritage have dedicated research views; others use generic entity view.
  const readerIds = ['houlun', 'qichuan']
  if (entryType === 'text' && readerIds.includes(id)) return `/research/entity/reader/${id}`
  if (entryType === 'person') return `/research/entity/person/${id}`
  if (entryType === 'work') return `/research/entity/work/${id}`
  if (entryType === 'edition') return `/research/entity/edition/${id}`
  if (entryType === 'archive') return `/research/entity/archive/${id}`
  if (entryType === 'paper') return `/research/entity/paper/${id}`
  return `/research/entity/${entryType}/${id}`
}
</script>

<template>
  <section aria-labelledby="research-search-heading">
    <h1 id="research-search-heading">研究检索</h1>
    <p class="research-search-intro">
      统一索引检索（与公众端共享同一数据索引）；研究端展示更高密度元数据。 论文题录：已结构化
      {{ SEARCHABLE_PAPER_TOTAL }} / 审计 {{ AUDITED_PAPER_TOTAL }}。
    </p>

    <form class="research-form" role="search" @submit.prevent="onSubmit">
      <label class="visually-hidden" for="research-q">检索词</label>
      <input
        id="research-q"
        v-model="inputValue"
        type="search"
        placeholder="例如：皇甫谧 / 甲乙经 / 黄龙祥"
      />
      <button type="submit">检索</button>
    </form>

    <template v-if="q">
      <p class="research-summary" role="status" aria-live="polite">
        找到 {{ filteredResults.length }} 条结果<template v-if="type !== 'all'"
          >（{{ searchTypeLabel(type) }}）</template
        >
      </p>

      <div class="research-layout">
        <aside class="research-facets" aria-label="筛选">
          <h2 class="research-facets__title">内容类型</h2>
          <button
            type="button"
            class="research-facet"
            :class="{ 'research-facet--active': type === 'all' }"
            :aria-pressed="type === 'all'"
            @click="onSelectType('all')"
          >
            <span>全部</span><span>{{ qResults.length }}</span>
          </button>
          <button
            v-for="facet in facets"
            :key="facet.type"
            type="button"
            class="research-facet"
            :class="{ 'research-facet--active': type === facet.type }"
            :aria-pressed="type === facet.type"
            @click="onSelectType(facet.type)"
          >
            <span>{{ facet.label }}</span
            ><span>{{ facet.count }}</span>
          </button>
        </aside>

        <ul v-if="filteredResults.length > 0" class="research-results">
          <li v-for="result in filteredResults" :key="result.entry.id" class="research-result">
            <p class="research-result__type">{{ searchTypeLabel(result.entry.type) }}</p>
            <p class="research-result__title">
              <a
                :href="researchHref(result.entry.type, result.entry.id)"
                class="research-result__link"
              >
                <SearchHighlight :text="result.entry.title" :query="q" />
              </a>
            </p>
            <p v-if="result.entry.subtitle" class="research-result__subtitle">
              <SearchHighlight :text="result.entry.subtitle" :query="q" />
            </p>
            <dl class="research-result__meta">
              <template v-if="result.entry.authors && result.entry.authors.length">
                <div>
                  <dt>作者/整理</dt>
                  <dd>{{ result.entry.authors.join('；') }}</dd>
                </div>
              </template>
              <template v-if="result.entry.year">
                <div>
                  <dt>年份</dt>
                  <dd>{{ result.entry.year }}</dd>
                </div>
              </template>
              <div>
                <dt>状态</dt>
                <dd>
                  {{
                    result.entry.status === 'AVAILABLE'
                      ? '已展示'
                      : result.entry.status === 'METADATA_ONLY'
                        ? '元数据已录'
                        : '整理中'
                  }}
                </dd>
              </div>
              <template v-if="result.entry.sourceName">
                <div>
                  <dt>来源</dt>
                  <dd>{{ result.entry.sourceName }}</dd>
                </div>
              </template>
            </dl>
            <p class="research-result__nav">
              <a v-if="result.entry.route" :href="result.entry.route">公众页 →</a>
              <a :href="researchHref(result.entry.type, result.entry.id)">研究视图 →</a>
            </p>
          </li>
        </ul>
        <div v-else class="research-empty" role="status">
          <p>未找到匹配「{{ q }}」的结果。</p>
          <p class="research-empty__hint">
            可尝试：人物名（皇甫谧 / 刘君奇）、作品名（甲乙经 / 帝王世纪）、整理者（黄龙祥）。
          </p>
        </div>
      </div>
    </template>
    <p v-else class="research-empty">输入检索词开始研究检索。</p>
  </section>
</template>

<style scoped>
.research-search-intro {
  color: var(--hfm-color-text-muted);
}

.research-form {
  display: flex;
  gap: var(--hfm-space-2);
  max-width: 42rem;
  margin: var(--hfm-space-3) 0 var(--hfm-space-5);
}

.research-form input {
  flex: 1;
  min-width: 0;
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
}

.research-form button {
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-citation);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-citation);
  cursor: pointer;
  font-weight: 600;
}

.research-summary {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-3);
}

.research-layout {
  display: grid;
  grid-template-columns: 11rem 1fr;
  gap: var(--hfm-space-5);
  align-items: start;
}

.research-facets {
  position: sticky;
  top: var(--hfm-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
}

.research-facets__title {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
  margin: 0 0 var(--hfm-space-1);
}

.research-facet {
  display: flex;
  justify-content: space-between;
  gap: var(--hfm-space-2);
  border: none;
  border-left: 3px solid transparent;
  background: none;
  padding: var(--hfm-space-1) var(--hfm-space-2);
  color: var(--hfm-color-text-secondary);
  cursor: pointer;
  text-align: left;
  font-size: var(--hfm-text-sm);
}

.research-facet:hover {
  background: var(--hfm-color-canvas);
  color: var(--hfm-color-text);
}

.research-facet--active {
  border-left-color: var(--hfm-color-citation);
  color: var(--hfm-color-citation);
  font-weight: 600;
}

.research-results {
  list-style: none;
  margin: 0;
  padding: 0;
}

.research-result {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.research-result__type {
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-azure);
  font-weight: 600;
}

.research-result__title {
  margin: 0;
  font-weight: 600;
}

.research-result__link {
  color: var(--hfm-color-text);
  text-decoration: none;
}

.research-result__link:hover {
  color: var(--hfm-color-accent);
}

.research-result__subtitle {
  margin: 0;
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.research-result__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-1) var(--hfm-space-5);
  margin: var(--hfm-space-1) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.research-result__meta div {
  display: flex;
  gap: var(--hfm-space-1);
}

.research-result__meta dt {
  font-weight: 600;
}

.research-result__meta dd {
  margin: 0;
}

.research-result__nav {
  display: flex;
  gap: var(--hfm-space-4);
  margin: var(--hfm-space-1) 0 0;
}

.research-result__nav a {
  color: var(--hfm-color-interactive);
  font-size: var(--hfm-text-sm);
  text-decoration: none;
}

.research-result__nav a:hover {
  text-decoration: underline;
}

.research-empty {
  color: var(--hfm-color-text-muted);
  padding: var(--hfm-space-6) 0;
}

.research-empty__hint {
  font-size: var(--hfm-text-sm);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}

@media (max-width: 767px) {
  .research-layout {
    grid-template-columns: 1fr;
  }

  .research-facets {
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .research-facet {
    border: 1px solid var(--hfm-color-border);
    border-left-width: 3px;
    border-radius: var(--hfm-radius-sm);
    padding: var(--hfm-space-1) var(--hfm-space-2);
  }
}
</style>
