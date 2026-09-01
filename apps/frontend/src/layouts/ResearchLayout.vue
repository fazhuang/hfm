<script setup lang="ts">
/**
 * ResearchLayout — UI-11 research shell (REFINE, not replace).
 * Same design system as public, higher metadata density. Keeps the
 * authenticated research role boundary (route guard unchanged) and logout.
 */
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppSkipLink from '../components/AppSkipLink.vue'
import ResearchSidebar from '../components/research/ResearchSidebar.vue'
import ResearchBreadcrumb from '../components/research/ResearchBreadcrumb.vue'

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
    <AppSkipLink />
    <header class="research-shell__header">
      <span class="research-shell__brand">皇甫谧数字人文 · 研究工作台</span>
      <nav class="research-shell__nav" aria-label="研究端账户导航">
        <RouterLink to="/research">研究工作台</RouterLink>
        <a href="/">公众门户</a>
        <button type="button" @click="onLogout">退出登录</button>
      </nav>
    </header>

    <div class="research-shell__body">
      <ResearchSidebar />
      <main id="main-content" class="research-shell__main" tabindex="-1">
        <ResearchBreadcrumb />
        <RouterView />
      </main>
    </div>
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
  padding: var(--hfm-space-3) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  background: var(--hfm-color-surface);
}

.research-shell__brand {
  font-weight: 600;
  font-family: var(--hfm-font-serif);
  color: var(--hfm-color-text);
}

.research-shell__nav {
  display: flex;
  gap: var(--hfm-space-4);
  align-items: center;
  font-size: var(--hfm-text-sm);
}

.research-shell__nav a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.research-shell__nav button {
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
  padding: var(--hfm-space-1) var(--hfm-space-3);
  cursor: pointer;
  font-size: var(--hfm-text-sm);
}

.research-shell__body {
  display: grid;
  grid-template-columns: 13rem 1fr;
  gap: var(--hfm-space-5);
  flex: 1;
  padding: var(--hfm-space-5) var(--hfm-space-6);
  align-items: start;
}

.research-shell__main {
  outline: none;
  max-width: 72rem;
}

@media (max-width: 767px) {
  .research-shell__body {
    grid-template-columns: 1fr;
  }

  .research-shell__header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--hfm-space-2);
  }
}
</style>
