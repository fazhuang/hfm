<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ApiError } from '../../services/api'
import { fetchHeritageLineage, visibleNodes, visibleRelations } from '../../services/heritage'
import type { LineageNode } from '../../types/heritage'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'
import LineageTree from '../../components/LineageTree.vue'

defineOptions({ name: 'HeritageView' })

const entityId = 'heritage-root'
const loading = ref(true)
const error = ref<string | null>(null)
const nodes = ref<LineageNode[]>([])

onMounted(async () => {
  try {
    const projection = await fetchHeritageLineage(entityId)
    // Public display: evidence-backed, published nodes and relations only.
    nodes.value = visibleNodes(projection)
    void visibleRelations(projection)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '无法加载传承谱系。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section aria-labelledby="heritage-heading">
    <h1 id="heritage-heading">传承谱系</h1>
    <p>仅展示有证据支撑且已获准发布的内容；未验证或非公开节点不会显示。</p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="nodes.length === 0" label="暂无已发布的传承谱系数据。" />
    <LineageTree v-else :nodes="nodes" />
  </section>
</template>
