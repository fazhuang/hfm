<script setup lang="ts">
/**
 * PublicLayout — public portal shell (UI-02 Global Shell / Navigation).
 *
 * TODO(UI 重构): 主导航目标见 HFM-UI-CONTRACT-v2 §2（参考图的 8 项），
 * 取代此前的"客户强制 5 链接"。Search + login live in the header utility area
 * (not part of the main nav); about lives in the main nav and the footer.
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

/**
 * 公众门户整站是**深色展厅面**（HFM-UI-CONTRACT-v2 §1：方案六 沉浸体验·未来展厅）。
 *
 * 页头与页脚是共享的，所以在**壳层**把语义色 token 换成展厅值 —— 页头、页脚，
 * 以及页面内任何用 `--hfm-color-*` 的地方一次性跟着变，不必逐个元素覆盖。
 * 研究端与后台用的是各自的 layout，不受影响。
 */
const surface = 'exhibition' as const

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
  <div class="public-shell" :data-surface="surface">
    <AppSkipLink />

    <header class="public-shell__header">
      <a class="public-shell__brand" href="/" aria-label="皇甫谧人文数字平台 首页">
        <!-- UI3-02C: frozen HFM Knowledge Mark (decorative). The adjacent text
             already names the brand link, so the symbol is not announced. -->
        <img
          class="public-shell__brand-symbol"
          src="/assets/brand/hfm-knowledge-mark-black.svg"
          alt=""
          aria-hidden="true"
        />
        <span class="public-shell__brand-text">
          <span class="public-shell__brand-mark" aria-hidden="true">皇甫谧</span>
          <span class="public-shell__brand-name">人文数字平台</span>
        </span>
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
        <form
          class="header-search"
          role="search"
          aria-label="全局检索"
          @submit.prevent="onSearchSubmit"
        >
          <label class="visually-hidden" for="header-search-input">检索平台内容</label>
          <input id="header-search-input" v-model="searchQuery" type="search" placeholder="检索…" />
          <button type="submit" class="header-search__submit">检索</button>
        </form>
        <p class="header-lang" aria-label="语言">
          <span class="header-lang__on">中</span>
          <span class="header-lang__sep" aria-hidden="true">|</span>
          <span class="header-lang__off" title="英文版尚未提供">EN</span>
        </p>
        <a class="header-workbench" href="/research">
          进入研究工作台
          <span aria-hidden="true">→</span>
        </a>
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

/* ---- 展厅面（首页）：整壳换深色 ----
   不在每个页头元素上逐个覆盖，而是**在这里把语义色 token 换成展厅值** ——
   页头、页脚、以及首页内任何用 --hfm-color-* 的地方一次性跟着变。
   作用域是 .public-shell[data-surface='exhibition']，只在 `/` 生效。 */
.public-shell[data-surface='exhibition'] {
  --hfm-color-canvas: #0f1211;
  --hfm-color-surface: #0f1211;
  --hfm-color-elevated: #1e2320;
  --hfm-color-text: #efede6;
  --hfm-color-text-secondary: #c9c5ba;
  /* 三级文字在近黑画布上要抬到 4.5:1 以上；#8a867c 只有 4.0:1。 */
  --hfm-color-text-muted: #9a958a;
  --hfm-color-border: rgba(239, 237, 230, 0.14);
  --hfm-color-border-strong: rgba(239, 237, 230, 0.3);
  --hfm-color-interactive: #dcab74;
  --hfm-color-accent: #c08a4e;
  /* 品牌字用的是 heritage，不是 accent —— 漏了这条它会落回浅色主题的值，
     在近黑画布上只有 3.75:1。提亮后的朱砂在此为 7.2:1。 */
  --hfm-color-heritage: #d98a6a;
  --hfm-color-heritage-surface: rgba(217, 138, 106, 0.12);
  /* 状态与语义色同理由：浅色模式下的深色值在近黑画布上全部不达标
     （warning #8a5a00 只有 2.4:1），这里各给一个暗场取值。 */
  --hfm-color-warning: #d9a441;
  --hfm-color-success: #6cc08a;
  --hfm-color-danger: #f0908a;
  --hfm-color-evidence: #6fbfa4;
  --hfm-color-citation: #9aa8d8;
  --hfm-color-azure: #9aa8b0;
  /* 状态胶囊用的是「亮底 + on-* 文字」。浅色模式的 on-* 是白字，
     在暗场里这些底已经变亮，白字全部不达标，改为墨字。 */
  --hfm-color-on-accent: #14100b;
  --hfm-color-on-heritage: #14100b;
  /* success 的浅底同理：浅色模式的 #e2f0e6 配暗场绿字只够 2.3:1。 */
  --hfm-color-success-surface: rgba(108, 192, 138, 0.16);
  background: var(--wl-paper);
  color: var(--wl-ink);
}
/* 页头并入画布，不留一条亮边把首屏切断。 */
.public-shell[data-surface='exhibition'] .public-shell__header {
  background: transparent;
  border-bottom-color: transparent;
}
/* 单色 mark 反白。图形本身只有 fill="#000" 一种填充，反色是干净的。 */
.public-shell[data-surface='exhibition'] .public-shell__brand-symbol {
  filter: invert(1);
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
  flex-direction: row;
  align-items: center;
  gap: var(--hfm-space-2);
  text-decoration: none;
  color: var(--hfm-color-text);
  white-space: nowrap;
  margin-right: var(--hfm-space-4);
}

.public-shell__brand-symbol {
  flex: none;
  width: 2.5rem;
  height: 2.5rem;
  display: block;
}

.public-shell__brand-text {
  display: flex;
  flex-direction: column;
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

/* ---- 语言标记（参考图：中 | EN）。EN 尚未提供，故不是链接。 ---- */
.header-lang {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-2);
  margin: 0;
  font-family: var(--wl-latin, ui-monospace, monospace);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.1em;
}
.header-lang__on {
  color: var(--hfm-color-text);
}
.header-lang__sep,
.header-lang__off {
  color: var(--hfm-color-text-muted);
}

/* ---- 研究工作台入口（参考图的工具区按钮） ---- */
.header-workbench {
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  padding: 0.4rem 0.9rem;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text);
  text-decoration: none;
  border: 1px solid var(--hfm-color-border-strong);
  border-radius: 2px;
}
.header-workbench:hover {
  border-color: var(--hfm-color-accent);
  color: var(--hfm-color-accent);
}
.header-workbench:focus-visible {
  outline: 2px solid var(--hfm-color-accent);
  outline-offset: 2px;
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
