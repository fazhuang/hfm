<script setup lang="ts">
/**
 * HomePersonSection — contract §4 block 02 (人物 / 皇甫谧).
 *
 * T0 (authoritative): GET /public/persons/ENT-PERSON-HFM-HUANGFUMI — the
 * admitted biographical assertions (predicate → value), rendered as ruled
 * account lines. T1 fallback: the customer-material core-person projection,
 * with a VISIBLE fallback note (contract §2 R3 / D3).
 */
import { computed } from 'vue'
import type { BlockData } from '../../composables/useHomeContractData'
import type { PublicPerson } from '../../types/public'
import {
  CORE_PERSON_DEFINITION,
  CORE_PERSON_IDENTITIES,
  CORE_PERSON_NAME,
} from '../../config/corePerson'

defineOptions({ name: 'HomePersonSection' })

const props = defineProps<{ block: BlockData<PublicPerson> }>()

/** T0: show the real assertions that carry a value (skip empty/relational ones). */
const assertions = computed(() =>
  (props.block.data?.assertions ?? []).filter((a) => (a.value ?? '').trim().length > 0),
)
const isBackend = computed(() => props.block.source === 'backend' && assertions.value.length > 0)
</script>

<template>
  <section id="home-person" class="xl-sec" aria-labelledby="home-person-title" :data-source="isBackend ? 'backend' : 'fallback'">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">02</span>
          <span class="xl-label">The Person</span>
        </div>
        <div>
          <h2 id="home-person-title" class="xl-title">皇甫谧</h2>
          <p class="xl-lede">{{ CORE_PERSON_DEFINITION }}</p>
        </div>
      </header>

      <!-- T0 — admitted assertions from the database -->
      <ol v-if="isBackend" class="person__facts xl-rows">
        <li v-for="(a, i) in assertions" :key="a.id" class="xl-row person__fact">
          <span class="xl-row__index">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="xl-row__body person__fact-body">
            <span class="person__fact-predicate">{{ a.predicate }}</span>
            <span class="person__fact-value">{{ a.value }}</span>
          </div>
        </li>
      </ol>

      <!-- T1 — visible fallback (customer-material projection) -->
      <div v-else class="person__fallback">
        <p class="fallback-note" data-fallback-note>
          数据库人物档案暂不可用 · 以下为离线兜底（客户材料）
        </p>
        <p class="person__identities">{{ CORE_PERSON_IDENTITIES.join(' · ') }}</p>
        <p class="person__name-static">{{ CORE_PERSON_NAME }}</p>
      </div>

      <p class="person__foot">
        <a class="home-person__act xl-go" href="/persons/ENT-PERSON-HFM-HUANGFUMI">
          进入人物档案 <span class="home-person__act-arr xl-go__arr" aria-hidden="true">→</span>
        </a>
      </p>
    </div>
  </section>
</template>

<style scoped>
.person__fact-body {
  display: grid;
  grid-template-columns: 9rem minmax(0, 1fr);
  gap: var(--hfm-space-5);
  align-items: baseline;
}
.person__fact-predicate {
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.12em;
  color: var(--wl-mark);
}
.person__fact-value {
  font-size: var(--hfm-text-base);
  line-height: 1.85;
  color: var(--wl-ink);
}
.person__fallback {
  padding: var(--hfm-space-6);
  border: 1px solid var(--wl-rule);
  background: var(--wl-light);
}
.fallback-note {
  margin: 0 0 var(--hfm-space-4);
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.08em;
  color: var(--wl-mark);
}
.person__identities {
  margin: 0 0 var(--hfm-space-2);
  font-size: var(--hfm-text-lg);
  color: var(--wl-ink);
}
.person__name-static {
  margin: 0;
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-3xl);
  color: var(--wl-ink);
}
.person__foot {
  margin: var(--hfm-space-6) 0 0;
}
@media (max-width: 900px) {
  .person__fact-body {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-1);
  }
}
</style>
