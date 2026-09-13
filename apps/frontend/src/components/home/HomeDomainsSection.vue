<script setup lang="ts">
/**
 * HomeDomainsSection — Section 07 (四域探索). 《刻度》 ledger voice:
 * four numbered entries, each a real route, carrying live published data when
 * the backend projection is present (REM-02 participation).
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
  <section id="home-domains" class="xl-sec xl-sec--dark" aria-labelledby="home-domains-title">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">{{ HOME_CHAPTERS.domains.no }}</span>
          <span class="xl-label">Explore</span>
        </div>
        <div>
          <h2 id="home-domains-title" class="xl-title">{{ HOME_DOMAINS.headline }}</h2>
          <p class="xl-lede">{{ HOME_DOMAINS.lede }}</p>
        </div>
      </header>

      <ul class="domains__grid xl-rows">
        <li v-for="domain in HOME_DOMAINS.domains" :key="domain.no" class="xl-row domains__card">
          <span class="xl-row__index">{{ domain.no }}</span>
          <div class="xl-row__body domains__card-body">
            <p class="domains__card-en xl-label">{{ domain.en }}</p>
            <h3 class="domains__card-title">{{ domain.title }}</h3>
            <p class="domains__card-key">{{ domain.key }}</p>

            <div v-if="published" class="domains__live">
              <template v-if="domain.no === '01' && published.counts.persons > 0">
                <p class="domains__live-row">
                  <b>已上线公开人物</b><span class="xl-num">{{ published.counts.persons }} 条档案</span>
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
                  <b>已上线公开术语</b><span class="xl-num">{{ published.counts.c_terms }} 条</span>
                </p>
              </template>
              <template v-else-if="domain.no === '04' && published.counts.heritage_projects > 0">
                <p class="domains__live-row">
                  <b>已上线公开传承档案</b>
                  <span class="xl-num">{{ published.counts.heritage_projects }} 项</span>
                </p>
              </template>
            </div>

            <a class="home-domains__go domains__card-cta xl-go" :href="domain.href">
              {{ domain.cta }}
              <span class="home-domains__go-arr domains__card-arr xl-go__arr" aria-hidden="true"
                >→</span
              >
            </a>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.domains__card-body {
  display: grid;
  gap: var(--hfm-space-2);
}
.domains__card-en {
  margin: 0;
}
.domains__card-title {
  margin: 0;
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-2xl);
  font-weight: 500;
  color: var(--wl-ink);
}
.domains__card-key {
  margin: 0 0 var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  color: var(--wl-mute);
}
.domains__live {
  margin: var(--hfm-space-2) 0;
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-left: 2px solid var(--wl-mark);
  background: var(--wl-light);
}
.domains__live-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-3);
  margin: 0;
  padding: var(--hfm-space-1) 0;
}
.domains__live-row b {
  font-size: var(--hfm-text-sm);
  font-weight: 500;
  color: var(--wl-ink);
}
.domains__live-row span {
  font-size: var(--hfm-text-xs);
  color: var(--wl-mute);
}
</style>
