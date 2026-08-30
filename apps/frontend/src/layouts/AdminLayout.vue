<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

defineOptions({ name: 'AdminLayout' })

const store = useAuthStore()
const router = useRouter()

async function onLogout(): Promise<void> {
  await store.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="admin-shell">
    <header class="admin-shell__header">
      <span class="admin-shell__brand">管理 / 发布控制台</span>
      <nav class="admin-shell__nav" aria-label="Admin navigation">
        <RouterLink to="/admin">发布管理</RouterLink>
        <button type="button" @click="onLogout">退出登录</button>
      </nav>
    </header>
    <main class="admin-shell__main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.admin-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--hfm-space-4) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  background: var(--hfm-color-surface);
}

.admin-shell__nav {
  display: flex;
  gap: var(--hfm-space-4);
  align-items: center;
}
</style>
