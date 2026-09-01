<script setup lang="ts">
/**
 * PublicLayout — public portal shell (UI-02 Global Shell / Navigation).
 *
 * Customer-mandated 5-link main navigation (首页 / 人物（皇甫谧）/ 其言 /
 * 《针灸甲乙经》 / 皇甫谧针灸非遗的传承). Search + login live in the
 * header utility area (not part of the main nav); about lives in the footer.
 * Mobile (<768px) collapses the nav into an accessible drawer: toggle with
 * aria-expanded, focus trap, Escape to close, focus restored.
 */
import { onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PUBLIC_NAV_ITEMS } from '../config/navigation'
import { useFocusTrap } from '../composables/useFocusTrap'
import AppSkipLink from '../components/AppSkipLink.vue'
import AppFooter from '../components/AppFooter.vue'

defineOptions({ name: 'PublicLayout' })

const route = useRoute()
const router = useRouter()

const drawerOpen = ref(false)
const toggleRef = ref<{ focus(): void } | null>(null)
const searchQuery = ref('')

const { containerRef: trapContainer, activate, deactivate } = useFocusTrap()

const isActive = (href: string): boolean => {
  // Defensive: layouts may render outside a router context (unit tests).
  const currentPath = route?.path ?? ''
  if (href === '/') return currentPath === '/'
  return currentPath.startsWith(href)
}

function onToggleDrawer(): void {
  if (drawerOpen.value) {
    closeDrawer()
  } else {
    drawerOpen.value = true
    // Attach the trap to the drawer panel (Tab cycles within the drawer).
    activate()
    // Escape must close the drawer regardless of where focus sits (toggle or
    // inside the panel).
    document.addEventListener('keydown', onGlobalKeydown)
  }
}

function closeDrawer(): void {
  if (!drawerOpen.value) return
  drawerOpen.value = false
  deactivate(toggleRef.value)
  document.removeEventListener('keydown', onGlobalKeydown)
}

function onGlobalKeydown(event: { key: string }): void {
  if (event.key === 'Escape') {
    closeDrawer()
  }
}

function onDrawerKeydown(event: { key: string }): void {
  if (event.key === 'Escape') {
    closeDrawer()
  }
}

function onSearchSubmit(): void {
  const q = searchQuery.value.trim()
  void router.push({ name: 'search', query: q ? { q } : {} })
}

onBeforeUnmount(() => {
  deactivate()
  document.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<template>
  <div class="public-shell">
    <AppSkipLink />

    <header class="public-shell__header">
      <a class="public-shell__brand" href="/" aria-label="皇甫谧人文数字平台 首页">
        <span class="public-shell__brand-mark" aria-hidden="true">皇甫谧</span>
        <span class="public-shell__brand-name">人文数字平台</span>
      </a>

      <button
        ref="toggleRef"
        type="button"
        class="nav-toggle"
        aria-label="打开导航菜单"
        :aria-expanded="drawerOpen"
        aria-controls="public-nav"
        @click="onToggleDrawer"
      >
        菜单
      </button>

      <nav
        id="public-nav"
        ref="trapContainer"
        class="public-shell__nav"
        aria-label="Public navigation"
        :class="{ 'public-shell__nav--open': drawerOpen }"
        @keydown="onDrawerKeydown"
      >
        <a
          v-for="item in PUBLIC_NAV_ITEMS"
          :key="item.href"
          class="nav-link"
          :class="{ 'nav-link--active': isActive(item.href) }"
          :href="item.href"
          :aria-current="isActive(item.href) ? 'page' : undefined"
          :aria-label="item.description"
          @click="closeDrawer"
        >
          {{ item.label }}
        </a>
      </nav>

      <div class="public-shell__tools">
        <form class="header-search" role="search" @submit.prevent="onSearchSubmit">
          <label class="visually-hidden" for="header-search-input">检索平台内容</label>
          <input id="header-search-input" v-model="searchQuery" type="search" placeholder="检索…" />
          <button type="submit" class="header-search__submit">检索</button>
        </form>
        <a class="header-login" href="/login">登录</a>
      </div>
    </header>

    <main id="main-content" class="public-shell__main" tabindex="-1">
      <RouterView />
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
.public-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.public-shell__header {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-4);
  padding: var(--hfm-space-4) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  background: var(--hfm-color-surface);
}

.public-shell__brand {
  display: flex;
  flex-direction: column;
  gap: 0;
  text-decoration: none;
  color: var(--hfm-color-text);
  white-space: nowrap;
  margin-right: var(--hfm-space-4);
}

.public-shell__brand-mark {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-xl);
  font-weight: 600;
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-heritage);
}

.public-shell__brand-name {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  letter-spacing: 0.08em;
}

.public-shell__nav {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-4);
  flex-wrap: wrap;
}

.nav-link {
  color: var(--hfm-color-text-secondary);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
  white-space: nowrap;
  padding: var(--hfm-space-1) 0;
  border-bottom: 2px solid transparent;
}

.nav-link:hover {
  color: var(--hfm-color-text);
}

.nav-link--active {
  color: var(--hfm-color-accent);
  border-bottom-color: var(--hfm-color-accent);
  font-weight: 600;
}

.public-shell__tools {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-3);
  margin-left: auto;
}

.header-search {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-2);
}

.header-search input {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  font-size: var(--hfm-text-sm);
  width: 9rem;
}

.header-search__submit {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
  font-size: var(--hfm-text-sm);
}

.header-login {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.header-login:hover {
  color: var(--hfm-color-accent-hover);
  text-decoration: underline;
}

.public-shell__main {
  flex: 1;
  padding: var(--hfm-space-6);
  outline: none;
}

.nav-toggle {
  display: none;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}

@media (max-width: 767px) {
  .public-shell__header {
    flex-wrap: wrap;
  }

  .nav-toggle {
    display: inline-flex;
    align-items: center;
    padding: var(--hfm-space-2) var(--hfm-space-3);
    border: 1px solid var(--hfm-color-border);
    border-radius: var(--hfm-radius-sm);
    background: var(--hfm-color-surface);
    color: var(--hfm-color-text);
    cursor: pointer;
    font-size: var(--hfm-text-sm);
  }

  /* Drawer: links hidden until opened; the <nav> element itself stays
     visible (holds the toggle target / a11y semantics). */
  .public-shell__nav {
    order: 3;
    flex-basis: 100%;
    display: none;
    flex-direction: column;
    align-items: stretch;
    gap: var(--hfm-space-1);
    border-top: 1px solid var(--hfm-color-border);
    padding-top: var(--hfm-space-3);
  }

  .public-shell__nav--open {
    display: flex;
  }

  .nav-link {
    white-space: normal;
    padding: var(--hfm-space-2) var(--hfm-space-3);
    border-bottom: none;
    border-left: 3px solid transparent;
  }

  .nav-link--active {
    border-left-color: var(--hfm-color-accent);
  }

  .public-shell__tools {
    order: 4;
    flex-basis: 100%;
    margin-left: 0;
  }
}
</style>
