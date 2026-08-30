<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

defineOptions({ name: 'ResearchLayout' })

const store = useAuthStore()
const router = useRouter()

async function onLogout(): Promise<void> {
  await store.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="research-shell">
    <header class="research-shell__header">
      <span class="research-shell__brand">校内研究后台</span>
      <nav class="research-shell__nav" aria-label="Research navigation">
        <RouterLink to="/research">研究工作台</RouterLink>
        <button type="button" @click="onLogout">退出登录</button>
      </nav>
    </header>
    <main class="research-shell__main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.research-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.research-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--hfm-space-4) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  background: var(--hfm-color-surface);
}

.research-shell__nav {
  display: flex;
  gap: var(--hfm-space-4);
  align-items: center;
}
</style>
