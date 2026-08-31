<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ApiError, fetchPublicHome, fetchPublicPersons } from '../services/api'
import EmptyState from '../components/states/EmptyState.vue'
import ErrorState from '../components/states/ErrorState.vue'
import LoadingState from '../components/states/LoadingState.vue'
import type { HomeCounts, PersonSummary, PublishedItem, WorkSummary } from '../types/public'
import { publishedOnly } from '../utils/publication'

const loading = ref(true)
const error = ref<string | null>(null)
const items = ref<PublishedItem[]>([])
const works = ref<WorkSummary[]>([])
const persons = ref<PersonSummary[]>([])
const counts = ref<HomeCounts | null>(null)

onMounted(async () => {
  try {
    const projection = await fetchPublicHome()
    items.value = publishedOnly(projection.items ?? [])
    works.value = projection.works ?? []
    counts.value = projection.counts ?? null
    if (projection.works?.length) {
      const personsData = await fetchPublicPersons().catch(() => null)
      if (personsData) persons.value = personsData.persons
    }
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : 'Unable to load public content.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section aria-labelledby="portal-heading">
    <div class="hero">
      <h1 id="portal-heading">皇甫谧人文数字平台 · 公开门户</h1>
      <p>
        公开门户只展示已获准发布的内容；未发布或已撤回内容不会出现在这里。平台为非商业非盈利的
        皇甫谧学术资料展示，仅供学术爱好者学习与宣传。
      </p>
      <a class="hero__cta" href="/library">进入资料库 →</a>
    </div>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />

    <template v-else>
      <div v-if="counts" class="stats" aria-label="平台内容统计">
        <div class="stats__card">
          <strong>{{ counts.works }}</strong
          ><span>已发布著作</span>
        </div>
        <div class="stats__card">
          <strong>{{ counts.persons }}</strong
          ><span>已发布人物</span>
        </div>
        <div class="stats__card">
          <strong>{{ counts.heritage_projects }}</strong
          ><span>传承谱系</span>
        </div>
        <div class="stats__card">
          <strong>{{ counts.c_terms }}</strong
          ><span>术语词条</span>
        </div>
      </div>

      <h2 class="section-title">著作</h2>
      <EmptyState v-if="works.length === 0" label="暂无已发布著作。" />
      <ul v-else class="portal-list">
        <li v-for="work in works" :key="work.work_id" class="portal-list__item">
          <a :href="`/works/${work.work_id}`" class="portal-list__link">
            <strong>{{ work.title }}</strong>
            <span class="muted">
              {{ work.dynasty || '—' }} · {{ work.category || '未分类' }} ·
              {{ work.edition_count }} 个版本
            </span>
          </a>
        </li>
      </ul>

      <h2 class="section-title">人物</h2>
      <EmptyState v-if="persons.length === 0" label="暂无已发布人物。" />
      <ul v-else class="portal-list">
        <li v-for="person in persons" :key="person.entity_id" class="portal-list__item">
          <a :href="`/persons/${person.entity_id}`" class="portal-list__link">
            <strong>{{ person.name_zh || '未命名' }}</strong>
            <span class="muted">{{ person.dynasty || '—' }}</span>
          </a>
        </li>
      </ul>

      <h2 class="section-title">公开内容</h2>
      <EmptyState v-if="items.length === 0" label="暂无已发布条目。" />
      <ul v-else class="portal-list">
        <li v-for="item in items" :key="item.id" class="portal-list__item">
          {{ item.title }}
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.hero {
  padding: var(--hfm-space-6);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-lg);
  background: var(--hfm-color-surface);
  margin-bottom: var(--hfm-space-5);
}

.hero h1 {
  margin: 0 0 var(--hfm-space-2);
}

.hero p {
  color: var(--hfm-color-text-muted);
  max-width: 60ch;
}

.hero__cta {
  display: inline-block;
  margin-top: var(--hfm-space-3);
  color: var(--hfm-color-accent);
  font-weight: 600;
  text-decoration: none;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--hfm-space-3);
  margin-bottom: var(--hfm-space-5);
}

.stats__card {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
}

.stats__card strong {
  font-size: var(--hfm-text-xl);
}

.stats__card span {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.section-title {
  margin: var(--hfm-space-5) 0 var(--hfm-space-3);
}

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

.portal-list__link {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
  color: var(--hfm-color-text);
  text-decoration: none;
}

.muted {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}
</style>
