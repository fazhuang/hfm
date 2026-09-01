<script setup lang="ts">
/**
 * ResearchBreadcrumb — reflects information architecture, not file paths.
 * e.g. 研究工作台 / 实体 / 作品 / 《针灸甲乙经》
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

defineOptions({ name: 'ResearchBreadcrumb' })

const route = useRoute()

const crumbs = computed<Array<{ label: string; href?: string }>>(() => {
  const base = { label: '研究工作台', href: '/research' }
  const path = route?.path ?? ''
  if (path.startsWith('/research/search')) {
    return [base, { label: '检索' }]
  }
  if (path.startsWith('/research/entity')) {
    const parts = path.split('/').filter(Boolean)
    const type = parts[2] ?? ''
    const id = parts[3] ?? ''
    const TYPE_LABEL: Record<string, string> = {
      person: '人物',
      work: '作品',
      edition: '版本',
      archive: '档案',
      paper: '论文',
      heritage: '非遗',
      reader: '文献',
    }
    return [
      base,
      { label: '实体' },
      { label: TYPE_LABEL[type] ?? type },
      ...(id ? [{ label: id }] : []),
    ]
  }
  return [base]
})
</script>

<template>
  <nav class="research-breadcrumb" aria-label="面包屑">
    <ol>
      <li v-for="(crumb, i) in crumbs" :key="i">
        <a v-if="crumb.href && i < crumbs.length - 1" :href="crumb.href">{{ crumb.label }}</a>
        <span v-else aria-current="page">{{ crumb.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.research-breadcrumb ol {
  list-style: none;
  margin: 0 0 var(--hfm-space-4);
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.research-breadcrumb li {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-2);
}

.research-breadcrumb li::after {
  content: '/';
  color: var(--hfm-color-text-muted);
}

.research-breadcrumb li:last-child::after {
  content: none;
}

.research-breadcrumb a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.research-breadcrumb a:hover {
  text-decoration: underline;
}
</style>
