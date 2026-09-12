<script setup lang="ts">
/**
 * ResearchSidebar — UI-11 research navigation (only real functions).
 * Mobile: collapsible drawer with focus trap, ESC close, focus return.
 */
import { onBeforeUnmount, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useFocusTrap } from '../../composables/useFocusTrap'

defineOptions({ name: 'ResearchSidebar' })

const route = useRoute()
const open = ref(false)
const toggleRef = ref<{ focus(): void } | null>(null)
const { containerRef, activate, deactivate } = useFocusTrap()

const NAV = [
  { label: '研究总览', href: '/research', match: '/research' },
  { label: '检索', href: '/research/search', match: '/research/search' },
  {
    label: '人物',
    href: '/research/entity/person/person-huangfu-mi',
    match: '/research/entity/person',
  },
  { label: '作品', href: '/research/entity/work/w-jiayi', match: '/research/entity/work' },
  {
    label: '版本',
    href: '/research/entity/edition/yitong-zhengmai-1601',
    match: '/research/entity/edition',
  },
  {
    label: '档案',
    href: '/research/entity/archive/a-jiayi-lunzhu',
    match: '/research/entity/archive',
  },
  { label: '论文', href: '/research/search?q=针灸甲乙经&type=paper', match: '' },
  { label: '非遗', href: '/research/entity/heritage/liujunqi', match: '/research/entity/heritage' },
  { label: '阅读', href: '/reader/houlun', match: '' },
] as const

function isActive(item: { match: string }): boolean {
  if (!item.match) return false
  return (route?.path ?? '').startsWith(item.match)
}

function toggle(): void {
  if (open.value) close()
  else {
    open.value = true
    activate()
    document.addEventListener('keydown', onGlobalKeydown)
  }
}

function close(): void {
  if (!open.value) return
  open.value = false
  deactivate(toggleRef.value)
  document.removeEventListener('keydown', onGlobalKeydown)
}

function onGlobalKeydown(event: { key: string }): void {
  if (event.key === 'Escape') close()
}

onBeforeUnmount(() => {
  deactivate()
  document.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<template>
  <nav class="research-sidebar" aria-label="研究导航">
    <button
      ref="toggleRef"
      type="button"
      class="research-sidebar__toggle"
      :aria-expanded="open"
      aria-controls="research-nav"
      @click="toggle"
    >
      {{ open ? '收起研究导航' : '研究导航' }}
    </button>

    <ul
      id="research-nav"
      ref="containerRef"
      class="research-sidebar__list"
      :class="{ 'research-sidebar__list--open': open }"
    >
      <li v-for="item in NAV" :key="item.href">
        <a
          :href="item.href"
          class="research-sidebar__link"
          :class="{ 'research-sidebar__link--active': isActive(item) }"
          :aria-current="isActive(item) ? 'page' : undefined"
          @click="close"
        >
          {{ item.label }}
        </a>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.research-sidebar__toggle {
  display: none;
  margin-bottom: var(--hfm-space-3);
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
  cursor: pointer;
}

.research-sidebar__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
}

.research-sidebar__link {
  display: block;
  padding: var(--hfm-space-1) var(--hfm-space-2);
  border-left: 3px solid transparent;
  color: var(--hfm-color-text-secondary);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.research-sidebar__link:hover {
  color: var(--hfm-color-text);
  background: var(--hfm-color-canvas);
}

.research-sidebar__link--active {
  border-left-color: var(--hfm-color-citation);
  color: var(--hfm-color-citation);
  font-weight: 600;
}

@media (max-width: 767px) {
  .research-sidebar__toggle {
    display: inline-flex;
  }

  .research-sidebar__list {
    display: none;
  }

  .research-sidebar__list--open {
    display: flex;
    border: 1px solid var(--hfm-color-border);
    border-radius: var(--hfm-radius-md);
    padding: var(--hfm-space-2);
  }
}
</style>
