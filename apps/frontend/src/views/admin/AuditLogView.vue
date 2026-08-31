<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { fetchAuditLog, fetchReconciliation } from '../../services/audit'
import type { AuditEntry, ReconciliationResult } from '../../services/audit'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'AuditLogView' })

const store = useAuthStore()
const entries = ref<AuditEntry[]>([])
const reconciliations = ref<ReconciliationResult[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    entries.value = await fetchAuditLog(store.token)
    reconciliations.value = await fetchReconciliation(store.token)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '无法加载审计日志。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section aria-labelledby="audit-heading">
    <h1 id="audit-heading">审计日志</h1>
    <p>只读视图：不可修改审计记录；非管理员角色无法访问。</p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />

    <template v-else>
      <h2>对账结果</h2>
      <ul class="reconciliation-list">
        <li v-for="r in reconciliations" :key="r.id" class="reconciliation-list__item">
          <span class="badge" :class="r.status === 'PASS' ? 'badge--pass' : 'badge--fail'">
            {{ r.status }}
          </span>
          {{ r.detail }}
        </li>
      </ul>
      <EmptyState v-if="reconciliations.length === 0" label="暂无对账记录。" />

      <h2>审计条目</h2>
      <ul class="audit-list">
        <li v-for="e in entries" :key="e.id" class="audit-list__item">
          <code>{{ e.action }}</code> → {{ e.targetType }}:{{ e.targetId }}
          <span class="audit-list__meta">{{ e.createdAt }}</span>
        </li>
      </ul>
      <EmptyState v-if="entries.length === 0" label="暂无审计条目。" />
    </template>
  </section>
</template>

<style scoped>
.badge {
  padding: var(--hfm-space-1) var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  font-size: var(--hfm-text-xs);
  font-weight: 600;
}

.badge--pass {
  background: #dcfce7;
  color: #166534;
}

.badge--fail {
  background: #fee2e2;
  color: #991b1b;
}

.reconciliation-list,
.audit-list {
  list-style: none;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.audit-list__item {
  display: grid;
  gap: var(--hfm-space-1);
}

.audit-list__meta {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}
</style>
