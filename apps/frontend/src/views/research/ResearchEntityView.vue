<script setup lang="ts">
/**
 * ResearchEntityView — UI-11 entity research view (person/work/edition/
 * archive/paper/heritage/reader). Driven by researchProjection over EXISTING
 * domain data. Research → Public links provided where a public page exists.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { researchEntity } from '../../data/researchProjection'
import EvidenceExplorer from '../../components/research/EvidenceExplorer.vue'
import RelatedEntityLinks from '../../components/research/RelatedEntityLinks.vue'

defineOptions({ name: 'ResearchEntityView' })

const route = useRoute()

const entity = computed(() => {
  const type = String(route?.params?.type ?? '')
  const id = String(route?.params?.id ?? '')
  return researchEntity(type, id)
})

const typeLabel = computed(() => {
  const type = String(route?.params?.type ?? '')
  const map: Record<string, string> = {
    person: '人物',
    work: '作品',
    edition: '版本',
    archive: '档案',
    paper: '论文',
    heritage: '非遗',
    reader: '文献',
  }
  return map[type] ?? '实体'
})
</script>

<template>
  <section aria-labelledby="entity-heading">
    <p class="entity-type">{{ typeLabel }} · 研究视图</p>

    <template v-if="!entity">
      <h1 id="entity-heading">未找到该实体</h1>
      <p>研究索引中不存在该实体，或尚未结构化。</p>
      <p>
        <a class="entity-link" href="/research">研究工作台</a>
        · <a class="entity-link" href="/research/search">研究检索</a>
      </p>
    </template>

    <template v-else>
      <h1 id="entity-heading" class="entity-title">{{ entity.title }}</h1>
      <p class="entity-subtitle">{{ entity.subtitle }}</p>

      <a v-if="entity.publicLink" :href="entity.publicLink.href" class="entity-public-link">
        → {{ entity.publicLink.label }}
      </a>

      <p v-if="entity.description" class="entity-desc">{{ entity.description }}</p>

      <h2 class="entity-section-title">元数据</h2>
      <dl class="entity-metadata">
        <div v-for="meta in entity.metadata" :key="meta.label">
          <dt>{{ meta.label }}</dt>
          <dd>{{ meta.value }}</dd>
        </div>
      </dl>

      <h2 class="entity-section-title">来源与版本上下文</h2>
      <dl class="entity-metadata">
        <div v-for="evidence in entity.evidence" :key="evidence.sourceName">
          <dt>来源</dt>
          <dd>{{ evidence.sourceName }}</dd>
        </div>
      </dl>

      <div v-if="entity.items && entity.items.length" class="entity-items">
        <h2 class="entity-section-title">记录</h2>
        <ul>
          <li v-for="item in entity.items" :key="item.title">
            {{ item.title }}<template v-if="item.meta"> · {{ item.meta }}</template>
          </li>
        </ul>
      </div>

      <EvidenceExplorer :evidence="entity.evidence" />
      <RelatedEntityLinks :links="entity.related" />
    </template>
  </section>
</template>

<style scoped>
.entity-type {
  margin: 0 0 var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.12em;
  color: var(--hfm-color-citation);
}

.entity-title {
  margin: 0 0 var(--hfm-space-2);
}

.entity-subtitle {
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-3);
}

.entity-public-link {
  display: inline-block;
  margin-bottom: var(--hfm-space-4);
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.entity-public-link:hover {
  text-decoration: underline;
}

.entity-desc {
  color: var(--hfm-color-text-secondary);
  line-height: var(--hfm-leading-normal);
  max-width: 72ch;
}

.entity-section-title {
  margin: var(--hfm-space-6) 0 var(--hfm-space-2);
  font-size: var(--hfm-text-base);
  padding-bottom: var(--hfm-space-1);
  border-bottom: 1px solid var(--hfm-color-border);
}

.entity-metadata {
  margin: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.entity-metadata div {
  display: grid;
  grid-template-columns: 9rem 1fr;
  gap: var(--hfm-space-3);
  padding: var(--hfm-space-1) 0;
  font-size: var(--hfm-text-sm);
}

.entity-metadata dt {
  color: var(--hfm-color-text-muted);
  font-weight: 600;
}

.entity-metadata dd {
  margin: 0;
  overflow-wrap: anywhere;
}

.entity-items ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.entity-items li {
  padding: var(--hfm-space-1) 0;
  border-bottom: 1px solid var(--hfm-color-border);
  font-size: var(--hfm-text-sm);
}

.entity-link {
  color: var(--hfm-color-interactive);
}

@media (max-width: 767px) {
  .entity-metadata div {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
