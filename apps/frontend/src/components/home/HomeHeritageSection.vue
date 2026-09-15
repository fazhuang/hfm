<script setup lang="ts">
/**
 * HomeHeritageSection — Section 06 (活态传承). 《刻度》 ledger voice:
 * the living transmission — ceremony plate, the carrier line, an honest
 * PARTIAL status, and the transmission traces as ruled entries.
 */
import { computed } from 'vue'
import { HOME_HERITAGE_LIVING, HOME_CHAPTERS } from '../../data/homeProjection'
import type { BlockData } from '../../composables/useHomeContractData'

defineOptions({ name: 'HomeHeritageSection' })

const props = defineProps<{ block?: BlockData<unknown[]> | null }>()

const person = HOME_HERITAGE_LIVING.person

/** T0 — published heritage projects; empty until C1 publishes them (contract §6). */
const t0Projects = computed(() =>
  props.block?.source === 'backend' ? (props.block.data ?? []) : [],
)
const hasT0 = computed(() => t0Projects.value.length > 0)
/** First N rendered; the block states the real total (contract §4: ≥1 T0 item). */
const shown = computed(() => t0Projects.value.slice(0, 6))
</script>

<template>
  <section id="home-heritage" class="xl-sec" aria-labelledby="home-heritage-title" :data-source="hasT0 ? 'backend' : 'fallback'">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">{{ HOME_CHAPTERS.heritage.no }}</span>
          <span class="xl-label">Living Heritage</span>
        </div>
        <div>
          <h2 id="home-heritage-title" class="xl-title">{{ HOME_HERITAGE_LIVING.headline }}</h2>
          <p class="heritage__project">{{ HOME_HERITAGE_LIVING.project }}</p>
        </div>
      </header>

      <!-- T0 — published heritage records (empty until C1) -->
      <ul v-if="hasT0" class="heritage__t0 xl-rows" data-source="backend">
        <li v-for="(proj, i) in shown" :key="i" class="xl-row heritage__t0-row">
          <span class="xl-row__index">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="xl-row__body heritage__t0-body">
            <span class="heritage__t0-name">
              {{ (proj as Record<string, unknown>).project_name ?? '' }}
            </span>
            <span class="heritage__t0-cat">
              {{ (proj as Record<string, unknown>).category ?? '' }}
            </span>
          </div>
        </li>
      </ul>
      <p v-if="hasT0 && t0Projects.length > shown.length" class="heritage__t0-more" data-t0-total>
        共 {{ t0Projects.length }} 项已发布非遗档案
      </p>
      <p v-else-if="!hasT0" class="fallback-note" data-fallback-note>
        数据库非遗档案尚未发布（待 C1 发布）· 以下为离线兜底（客户材料）
      </p>

      <div class="heritage__grid">
        <figure class="heritage__visual">
          <img
            src="/assets/heritage/heritage-baishi-ceremony.jpg"
            alt="皇甫谧针灸师承教育拜师大会"
          />
        </figure>

        <div class="heritage__body">
          <p class="heritage__person">
            <span class="heritage__person-gen xl-label">{{ person.generationTitle }}</span>
            <span class="heritage__person-name">{{ person.name }}</span>
          </p>
          <p class="heritage__role">{{ person.heritageRole }}</p>

          <p class="heritage__lineage">
            <span class="hfm-status" data-status="PARTIAL">谱系整理中</span>
            <span class="heritage__lineage-note">{{ HOME_HERITAGE_LIVING.lineageNote }}</span>
          </p>

          <ul class="heritage__traces xl-rows">
            <li
              v-for="(trace, i) in HOME_HERITAGE_LIVING.traces"
              :key="trace.title"
              class="xl-row heritage__trace"
            >
              <span class="xl-row__index">{{ String(i + 1).padStart(2, '0') }}</span>
              <div class="xl-row__body heritage__trace-body">
                <a class="heritage__trace-link" :href="trace.href">{{ trace.title }}</a>
                <span class="heritage__trace-meta">{{ trace.meta }}</span>
              </div>
            </li>
          </ul>

          <a class="home-heritage__act heritage__cta xl-go" :href="HOME_HERITAGE_LIVING.cta.href">
            {{ HOME_HERITAGE_LIVING.cta.label }}
            <span class="home-heritage__act-arr heritage__cta-arr xl-go__arr" aria-hidden="true"
              >→</span
            >
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.heritage__project {
  margin: var(--hfm-space-4) 0 0;
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.06em;
  color: var(--wl-mute);
}
.heritage__t0 {
  margin-bottom: var(--hfm-space-12);
}
.heritage__t0-body {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-4);
  flex-wrap: wrap;
}
.heritage__t0-name {
  font-size: var(--hfm-text-base);
  color: var(--wl-ink);
}
.heritage__t0-more {
  margin: calc(-1 * var(--hfm-space-4)) 0 var(--hfm-space-8);
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.06em;
  color: var(--wl-mark);
}
.heritage__t0-cat {
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  color: var(--wl-mute);
}
.heritage__grid {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  gap: clamp(2rem, 5vw, 4rem);
  align-items: start;
}
.heritage__visual {
  margin: 0;
  border: 1px solid var(--wl-rule);
  overflow: hidden;
}
.heritage__visual img {
  display: block;
  width: 100%;
  height: auto;
}
.heritage__body {
  min-width: 0;
}
.heritage__person {
  display: flex;
  align-items: baseline;
  gap: var(--hfm-space-3);
  margin: 0 0 var(--hfm-space-2);
}
.heritage__person-name {
  font-family: var(--hfm-font-heading);
  font-size: clamp(1.75rem, 3.6vw, 2.5rem);
  color: var(--wl-ink);
}
.heritage__role {
  margin: 0 0 var(--hfm-space-6);
  font-size: var(--hfm-text-sm);
  color: var(--wl-ink-2);
}
.heritage__lineage {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin: 0 0 var(--hfm-space-8);
  padding: var(--hfm-space-4);
  border: 1px solid var(--wl-rule);
  background: var(--wl-light);
}
.heritage__lineage :deep(.hfm-status[data-status='PARTIAL']) {
  background: var(--wl-mark);
  color: var(--wl-paper);
}
.heritage__lineage-note {
  font-size: var(--hfm-text-sm);
  color: var(--wl-ink-2);
}
.heritage__traces {
  margin: 0 0 var(--hfm-space-8);
}
.heritage__trace-body {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-4);
  flex-wrap: wrap;
}
.heritage__trace-link {
  font-size: var(--hfm-text-base);
  color: var(--wl-ink);
  text-decoration: none;
}
.heritage__trace-link:hover {
  color: var(--wl-mark);
}
.heritage__trace-meta {
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  color: var(--wl-mute);
}
@media (max-width: 900px) {
  .heritage__grid {
    grid-template-columns: 1fr;
  }
  .heritage__visual {
    max-width: 30rem;
  }
}
</style>
