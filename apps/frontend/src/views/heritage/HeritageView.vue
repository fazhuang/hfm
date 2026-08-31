<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ApiError, publicGet } from '../../services/api'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'HeritageView' })

interface HeritageRelation {
  relation_id: string
  subject_entity_id: string
  subject_name: string | null
  relation_role: string
  official_name: string | null
  evidence_id: string | null
}

const loading = ref(true)
const error = ref<string | null>(null)
const projectName = ref('')
const relations = ref<HeritageRelation[]>([])

const ROLE_LABELS: Record<string, string> = {
  master: '师从',
  disciple: '传于',
  inheritor: '传承',
  subject: '主体',
  institution: '机构',
  other: '关联',
}

onMounted(async () => {
  try {
    const projects = await publicGet<{
      projects: Array<{ entity_id: string; project_name: string }>
    }>('/api/v1/public/heritage')
    if (projects.projects.length === 0) {
      return
    }
    const project = projects.projects[0]
    projectName.value = project.project_name
    const lineage = await publicGet<{ relations: HeritageRelation[] }>(
      `/api/v1/public/heritage/${project.entity_id}`,
    )
    relations.value = lineage.relations.filter((r) => r.evidence_id !== null)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '传承谱系加载失败。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section aria-labelledby="heritage-heading">
    <h1 id="heritage-heading">传承谱系</h1>
    <p class="heritage-intro">
      展示证据完备的传承关系（仅公开已发布、带证据的谱系；演示数据依据《晋书》皇甫谧传）。
    </p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="relations.length === 0" label="暂无已发布的传承谱系数据。" />

    <div v-else>
      <h2 class="project-name">{{ projectName }}</h2>
      <ul class="lineage">
        <li v-for="relation in relations" :key="relation.relation_id" class="lineage__item">
          <span class="lineage__subject">{{ relation.subject_name || '未命名' }}</span>
          <span class="lineage__role">{{
            ROLE_LABELS[relation.relation_role] || relation.relation_role
          }}</span>
          <span class="lineage__desc">{{ relation.official_name || '' }}</span>
        </li>
      </ul>
      <p class="heritage-note">
        皇甫谧 ·
        师从席坦（《晋书》：「就乡人席坦受书」）；子皇甫方回承其学。证据来源：客户《其传》资料。
      </p>
    </div>
  </section>
</template>

<style scoped>
.heritage-intro {
  color: var(--hfm-color-text-muted);
}

.project-name {
  margin: var(--hfm-space-4) 0;
}

.lineage {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-3);
}

.lineage__item {
  display: flex;
  align-items: baseline;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.lineage__subject {
  font-weight: 700;
  font-size: var(--hfm-text-lg);
}

.lineage__role {
  font-size: var(--hfm-text-xs);
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-bg);
  color: var(--hfm-color-text-muted);
}

.lineage__desc {
  color: var(--hfm-color-text-muted);
}

.heritage-note {
  margin-top: var(--hfm-space-4);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}
</style>
