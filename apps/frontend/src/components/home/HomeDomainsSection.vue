<script setup lang="ts">
/**
 * HomeDomainsSection — homepage Section 07 (四域探索 / research navigation).
 *
 * REDESIGN: four editorial entry cards on the warm canvas, consistent with the
 * redesigned hero. Real routes only (no fake links).
 *
 * LIVE PARTICIPATION (REM-02): when the backend home projection carries
 * non-empty published data, it participates visibly inside the matching door —
 * 已上线公开人物 / 已发布文献 / 已上线公开术语 / 已上线公开传承档案 — without
 * inventing content or changing the frozen structure.
 *
 * CONTRACT PRESERVED (ui03_home.spec.ts / rem02_home_public.spec.ts): <section
 * id="home-domains"> with the single H2 「四域探索」; the rejected NARRATIVE →
 * USABLE ARCHIVE line never returns; the four routes stay real.
 */
import { computed } from 'vue'
import { HOME_DOMAINS, HOME_CHAPTERS } from '../../data/homeProjection'
import type { HomePublicEnrichment } from '../../data/homePublicEnrichment'

defineOptions({ name: 'HomeDomainsSection' })

const props = withDefaults(defineProps<{ published?: HomePublicEnrichment | null }>(), {
  published: null,
})

const publishedWorks = computed(() => (props.published?.works ?? []).slice(0, 2))
</script>

<template>
  <section id="home-domains" class="domains" aria-labelledby="home-domains-title">
    <div class="domains__inner">
      <header class="domains__head">
        <p class="domains__eyebrow">
          <span class="domains__no">{{ HOME_CHAPTERS.domains.no }}</span
          >{{ HOME_CHAPTERS.domains.label }}
        </p>
        <h2 id="home-domains-title" class="domains__title">{{ HOME_DOMAINS.headline }}</h2>
        <p class="domains__lede">{{ HOME_DOMAINS.lede }}</p>
      </header>

      <ul class="domains__grid">
        <li v-for="domain in HOME_DOMAINS.domains" :key="domain.no" class="domains__card">
          <p class="domains__card-no" aria-hidden="true">{{ domain.no }}</p>
          <p class="domains__card-en">{{ domain.en }}</p>
          <h3 class="domains__card-title">{{ domain.title }}</h3>
          <p class="domains__card-key">{{ domain.key }}</p>

          <!-- live backend participation (only when published data is present) -->
          <div v-if="published" class="domains__live">
            <template v-if="domain.no === '01' && published.counts.persons > 0">
              <p class="domains__live-row">
                <b>已上线公开人物</b><span>{{ published.counts.persons }} 条档案</span>
              </p>
            </template>
            <template v-else-if="domain.no === '02' && publishedWorks.length > 0">
              <p v-for="row in publishedWorks" :key="row.work_id" class="domains__live-row">
                <b>{{ row.title }}</b>
                <span>{{ row.dynasty ? row.dynasty + ' · 已发布文献' : '已发布文献' }}</span>
              </p>
            </template>
            <template v-else-if="domain.no === '03' && published.counts.c_terms > 0">
              <p class="domains__live-row">
                <b>已上线公开术语</b><span>{{ published.counts.c_terms }} 条</span>
              </p>
            </template>
            <template v-else-if="domain.no === '04' && published.counts.heritage_projects > 0">
              <p class="domains__live-row">
                <b>已上线公开传承档案</b>
                <span>{{ published.counts.heritage_projects }} 项</span>
              </p>
            </template>
          </div>

          <a class="home-domains__go domains__card-cta" :href="domain.href">
            {{ domain.cta }} <span class="home-domains__go-arr domains__card-arr" aria-hidden="true">→</span>
          </a>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.domains {
  background: var(--hfm-color-canvas);
  padding: var(--hfm-space-24) var(--hfm-space-6);
}
.domains__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}
.domains__head {
  max-width: 44rem;
  margin-bottom: var(--hfm-space-16);
}
.domains__eyebrow {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.4em;
  color: var(--hfm-color-heritage);
}
.domains__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.domains__title {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--hfm-font-heading);
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 500;
  line-height: var(--hfm-leading-tight);
  color: var(--hfm-color-text);
}
.domains__lede {
  margin: 0;
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-secondary);
}
.domains__grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--hfm-space-8);
}
.domains__card {
  display: flex;
  flex-direction: column;
  padding-top: var(--hfm-space-6);
  border-top: 1px solid var(--hfm-color-border-strong);
}
.domains__card-no {
  margin: 0 0 var(--hfm-space-3);
  font-family: var(--hfm-font-numeric);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-heritage);
}
.domains__card-en {
  margin: 0 0 var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.24em;
  color: var(--hfm-color-text-muted);
}
.domains__card-title {
  margin: 0 0 var(--hfm-space-1);
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-xl);
  font-weight: 500;
  color: var(--hfm-color-text);
}
.domains__card-key {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

/* live backend participation */
.domains__live {
  margin-bottom: var(--hfm-space-4);
  padding: var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
}
.domains__live-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin: 0;
  padding: var(--hfm-space-1) 0;
}
.domains__live-row + .domains__live-row {
  border-top: 1px solid var(--hfm-color-border);
}
.domains__live-row b {
  font-size: var(--hfm-text-sm);
  font-weight: 500;
  color: var(--hfm-color-evidence);
}
.domains__live-row span {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.domains__card-cta {
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  margin-top: auto;
  padding-top: var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.08em;
  color: var(--hfm-color-accent);
  text-decoration: none;
}
.domains__card-arr {
  transition: transform 0.18s ease;
}
.domains__card-cta:hover .domains__card-arr {
  transform: translateX(3px);
}
@media (max-width: 1023px) {
  .domains__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 599px) {
  .domains {
    padding: var(--hfm-space-16) var(--hfm-space-4);
  }
  .domains__grid {
    grid-template-columns: 1fr;
  }
}
</style>
