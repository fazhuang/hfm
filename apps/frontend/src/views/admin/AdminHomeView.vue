<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { adminActions } from '../../services/admin'

defineOptions({ name: 'AdminHomeView' })

const store = useAuthStore()
const result = ref<string | null>(null)
const error = ref<string | null>(null)

async function publishDemo(): Promise<void> {
  error.value = null
  result.value = null
  try {
    // Publish action goes through the audit-logged admin endpoint (P1-09).
    const response = await adminActions.publish('demo-artifact', store.token)
    result.value = `published: ${response.publication_status}`
  } catch {
    error.value = '发布操作失败（可能权限不足或会话已失效）。'
  }
}
</script>

<template>
  <section aria-labelledby="admin-heading">
    <h1 id="admin-heading">发布管理</h1>
    <p>管理面基础：仅限内容审核/管理员角色；所有发布与撤回操作均走审计端点。</p>
    <button type="button" @click="publishDemo">发布演示条目</button>
    <p v-if="result" class="ok" role="status">{{ result }}</p>
    <p v-if="error" class="err" role="alert">{{ error }}</p>
  </section>
</template>

<style scoped>
.ok {
  color: var(--hfm-color-accent);
}

.err {
  color: var(--hfm-color-danger);
}
</style>
