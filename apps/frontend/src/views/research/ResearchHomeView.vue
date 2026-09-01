<script setup lang="ts">
/**
 * ResearchHomeView — UI-11 research landing.
 * Answers "我可以研究什么？" with REAL inventory. ExportPanel (P2-06)
 * stays intact. No fake user-behavior statistics.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ExportPanel from '../../components/ExportPanel.vue'
import { researchScopeSummary } from '../../data/researchProjection'
import { SEARCHABLE_PAPER_TOTAL, AUDITED_PAPER_TOTAL } from '../../data/researchProjection'

defineOptions({ name: 'ResearchHomeView' })

const router = useRouter()
const searchInput = ref('')

const scope = researchScopeSummary()

function onSearch(): void {
  const q = searchInput.value.trim()
  void router.push({ path: '/research/search', query: q ? { q } : {} })
}
</script>

<template>
  <section aria-labelledby="research-heading">
    <h1 id="research-heading">研究工作台</h1>
    <p class="research-intro">
      数字人文研究工作台：检索、实体浏览、Evidence、引用与研究导航。
      研究端展示为高密度元数据呈现；RBAC 与研究边界保持正式契约。
    </p>

    <!-- Search entry -->
    <form class="research-search" role="search" @submit.prevent="onSearch">
      <label class="visually-hidden" for="research-search-input">检索研究内容</label>
      <input
        id="research-search-input"
        v-model="searchInput"
        type="search"
        placeholder="检索人物 / 作品 / 版本 / 档案 / 论文…"
      />
      <button type="submit">检索</button>
    </form>

    <!-- Content scope summary (real inventory) -->
    <section aria-labelledby="scope-heading">
      <h2 id="scope-heading" class="section-title">可研究内容</h2>
      <dl class="scope-grid">
        <div v-for="item in scope" :key="item.label" class="scope-item">
          <dt>{{ item.label }}</dt>
          <dd>
            <a v-if="item.href" :href="item.href">{{ item.value }}</a>
            <template v-else>{{ item.value }}</template>
          </dd>
        </div>
      </dl>
      <p class="research-note">
        论文：审计 {{ AUDITED_PAPER_TOTAL }} 篇，已结构化题录 {{ SEARCHABLE_PAPER_TOTAL }} 条
        （PAPER_BIBLIOGRAPHY_STRUCTURING: PARTIAL——不宣称 515 篇全部可检索/引用）。
      </p>
    </section>

    <!-- Evidence / Citation / Reader access -->
    <section aria-labelledby="access-heading">
      <h2 id="access-heading" class="section-title">Evidence · 引用 · 阅读</h2>
      <ul class="access-list">
        <li>
          <a href="/research/entity/reader/houlun">后论 · 历史评价汇编（含 12 条可引用引文）</a>
        </li>
        <li><a href="/research/entity/reader/qichuan">其传 · 史料来源整理</a></li>
        <li><a href="/research/entity/person/person-huangfu-mi">皇甫谧研究视图</a></li>
        <li>
          <a href="/research/entity/heritage/liujunqi"
            >皇甫谧针灸非遗研究视图（第六代名医·刘君奇）</a
          >
        </li>
      </ul>
    </section>

    <!-- P2-06 export surface (keep intact) -->
    <section aria-labelledby="export-heading">
      <h2 id="export-heading" class="section-title">导出</h2>
      <ExportPanel />
    </section>
  </section>
</template>

<style scoped>
.research-intro {
  color: var(--hfm-color-text-muted);
  max-width: 72ch;
}

.research-search {
  display: flex;
  gap: var(--hfm-space-2);
  margin: var(--hfm-space-4) 0 var(--hfm-space-8);
  max-width: 42rem;
}

.research-search input {
  flex: 1;
  min-width: 0;
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
}

.research-search button {
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-citation);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-citation);
  cursor: pointer;
  font-weight: 600;
}

.section-title {
  margin: 0 0 var(--hfm-space-3);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.scope-grid {
  margin: 0 0 var(--hfm-space-3);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--hfm-space-2);
}

.scope-item {
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
}

.scope-item dt {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.scope-item dd {
  margin: 0;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.scope-item a {
  color: var(--hfm-color-text);
  text-decoration: none;
}

.scope-item a:hover {
  color: var(--hfm-color-accent);
}

.research-note {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.access-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.access-list li {
  padding: var(--hfm-space-1) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.access-list a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.access-list a:hover {
  text-decoration: underline;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
</style>
