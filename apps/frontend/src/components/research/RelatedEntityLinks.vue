<script setup lang="ts">
/**
 * RelatedEntityLinks — UI-11 contextual entity navigation.
 * Renders only confirmed relations (from existing data hrefs).
 */
import type { ResearchRelatedLink } from '../../types/research'

defineOptions({ name: 'RelatedEntityLinks' })

defineProps<{ links: ResearchRelatedLink[] }>()
</script>

<template>
  <nav v-if="links.length > 0" class="related-entity" aria-label="相关实体">
    <h2 class="related-entity__title">相关</h2>
    <ul class="related-entity__list">
      <li v-for="link in links" :key="link.href">
        <a :href="link.href" class="related-entity__link">{{ link.label }}</a>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.related-entity {
  margin-top: var(--hfm-space-5);
}

.related-entity__title {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
  margin: 0 0 var(--hfm-space-2);
}

.related-entity__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.related-entity__link {
  color: var(--hfm-color-interactive);
  font-size: var(--hfm-text-sm);
  text-decoration: none;
}

.related-entity__link:hover {
  text-decoration: underline;
}
</style>
