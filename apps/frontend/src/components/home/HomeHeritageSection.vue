<script setup lang="ts">
/**
 * HomeHeritageSection — homepage Section 06 (活态传承 / living transmission).
 *
 * REDESIGN: the living-transmission section — an editorial head, the
 * documentary ceremony image, the 第六代名医·刘君奇 profile line, an honest
 * PARTIAL status pill (谱系整理中), the documentary traces, and a heritage
 * archive CTA.
 *
 * CONTRACT PRESERVED (ui03_home.spec.ts): <section id="home-heritage"> with the
 * single H2 「一千七百年之后，传承仍在继续。」; .hfm-status[data-status=PARTIAL]
 * reading 谱系整理中; the section text carries 第六代名医 and 刘君奇; real
 * /heritage route. No fabricated lineage.
 */
import { HOME_HERITAGE_LIVING, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeHeritageSection' })

const person = HOME_HERITAGE_LIVING.person
</script>

<template>
  <section id="home-heritage" class="heritage" aria-labelledby="home-heritage-title">
    <div class="heritage__inner">
      <header class="heritage__head">
        <p class="heritage__eyebrow">
          <span class="heritage__no">{{ HOME_CHAPTERS.heritage.no }}</span
          >{{ HOME_CHAPTERS.heritage.label }}
        </p>
        <h2 id="home-heritage-title" class="heritage__title">
          {{ HOME_HERITAGE_LIVING.headline }}
        </h2>
        <p class="heritage__project">{{ HOME_HERITAGE_LIVING.project }}</p>
      </header>

      <div class="heritage__grid">
        <figure class="heritage__visual">
          <img
            src="/assets/heritage/heritage-baishi-ceremony.jpg"
            alt="皇甫谧针灸师承教育拜师大会"
          />
        </figure>

        <div class="heritage__body">
          <p class="heritage__person">
            <span class="heritage__person-gen">{{ person.generationTitle }}</span>
            <span class="heritage__person-name">{{ person.name }}</span>
          </p>
          <p class="heritage__role">{{ person.heritageRole }}</p>

          <p class="heritage__lineage">
            <span class="hfm-status" data-status="PARTIAL">谱系整理中</span>
            <span class="heritage__lineage-note">{{ HOME_HERITAGE_LIVING.lineageNote }}</span>
          </p>

          <ul class="heritage__traces">
            <li
              v-for="trace in HOME_HERITAGE_LIVING.traces"
              :key="trace.title"
              class="heritage__trace"
            >
              <a class="heritage__trace-link" :href="trace.href">{{ trace.title }}</a>
              <span class="heritage__trace-meta">{{ trace.meta }}</span>
            </li>
          </ul>

          <a class="home-heritage__act heritage__cta" :href="HOME_HERITAGE_LIVING.cta.href">
            {{ HOME_HERITAGE_LIVING.cta.label }}
            <span class="home-heritage__act-arr heritage__cta-arr" aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.heritage {
  background: var(--hfm-color-surface);
  padding: var(--hfm-space-24) var(--hfm-space-6);
}
.heritage__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}
.heritage__head {
  max-width: 44rem;
  margin-bottom: var(--hfm-space-12);
}
.heritage__eyebrow {
  margin: 0 0 var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.4em;
  color: var(--hfm-color-heritage);
}
.heritage__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.heritage__title {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  line-height: var(--hfm-leading-tight);
  color: var(--hfm-color-text);
}
.heritage__project {
  margin: 0;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.08em;
  color: var(--hfm-color-text-muted);
}
.heritage__grid {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: var(--hfm-space-16);
  align-items: start;
}
.heritage__visual {
  margin: 0;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
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
.heritage__person-gen {
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.16em;
  color: var(--hfm-color-heritage);
}
.heritage__person-name {
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-2xl);
  color: var(--hfm-color-text);
}
.heritage__role {
  margin: 0 0 var(--hfm-space-6);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}
.heritage__lineage {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin: 0 0 var(--hfm-space-8);
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-canvas);
}
.heritage__lineage-note {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}
.heritage__traces {
  list-style: none;
  margin: 0 0 var(--hfm-space-8);
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}
.heritage__trace {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-4);
  padding-bottom: var(--hfm-space-3);
  border-bottom: 1px solid var(--hfm-color-border);
}
.heritage__trace-link {
  font-size: var(--hfm-text-base);
  color: var(--hfm-color-text);
  text-decoration: none;
}
.heritage__trace-link:hover {
  color: var(--hfm-color-accent);
}
.heritage__trace-meta {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  text-align: right;
}
.heritage__cta {
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  color: var(--hfm-color-accent);
  text-decoration: none;
}
.heritage__cta-arr {
  transition: transform 0.18s ease;
}
.heritage__cta:hover .heritage__cta-arr {
  transform: translateX(3px);
}

/* PARTIAL status pill (shared .hfm-status has no PARTIAL variant) */
.heritage__lineage :deep(.hfm-status[data-status='PARTIAL']) {
  background: var(--hfm-color-warning);
  color: var(--hfm-color-on-accent);
}

@media (max-width: 1023px) {
  .heritage__grid {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-12);
  }
  .heritage__visual {
    max-width: 32rem;
  }
}
@media (max-width: 599px) {
  .heritage {
    padding: var(--hfm-space-16) var(--hfm-space-4);
  }
}
</style>
