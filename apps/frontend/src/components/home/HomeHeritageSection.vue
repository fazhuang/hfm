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
  <section
    id="home-heritage"
    class="xl-sec"
    aria-labelledby="home-heritage-title"
    :data-source="hasT0 ? 'backend' : 'fallback'"
  >
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">05</span>
          <span class="xl-label">Living Heritage</span>
        </div>
        <div>
          <h2 id="home-heritage-title" class="xl-title">{{ HOME_HERITAGE_LIVING.headline }}</h2>
          <p class="xl-lede">
            {{ HOME_HERITAGE_LIVING.project }} —— 师承教育、非遗佐证与地域文化，
            传承不是名词，是正在发生的事。
          </p>
        </div>
      </header>

      <!-- 三张真实材料。图注如实说明它是什么，不借题发挥。 -->
      <ul class="xl-cards">
        <li>
          <a class="xl-card" href="/heritage">
            <img src="/assets/heritage/heritage-baishi-ceremony.jpg" alt="皇甫谧学院师承教育拜师大会现场" />
            <span class="xl-card__caption">
              <span class="xl-card__en">Education</span>
              <span class="xl-card__title">师承教育</span>
              <span class="xl-card__note">皇甫谧学院师承教育拜师大会 · 客户提供照片</span>
            </span>
          </a>
        </li>
        <li>
          <a class="xl-card" href="/heritage">
            <img src="/assets/heritage/01a099de-6383-75b4-8932-3fb563a12d78.jpg" alt="非遗佐证材料" />
            <span class="xl-card__caption">
              <span class="xl-card__en">Intangible Heritage</span>
              <span class="xl-card__title">非遗佐证</span>
              <span class="xl-card__note">央视《魅力中国城》栏目参与证明材料 · 客户提供</span>
            </span>
          </a>
        </li>
        <li>
          <a class="xl-card" href="/jiayi">
            <img src="/assets/jiayi/book-siku-leaf.jpg" alt="四库全书本《针灸甲乙经》书叶" />
            <span class="xl-card__caption">
              <span class="xl-card__en">The Classics</span>
              <span class="xl-card__title">典籍版本</span>
              <span class="xl-card__note">四库全书本书叶 · 客户授权资料</span>
            </span>
          </a>
        </li>
      </ul>

      <!-- 本段只讲「今天还在发生什么」：三张真实材料就是内容本身。
           此前还并列六行台账登记，等于把传承档案页搬了过来。
           T0 数据由这一行总数承载（契约 §4 要求每段至少一条真实投影）。 -->
      <p v-if="hasT0" class="heritage__t0-total" data-t0-total data-source="backend">
        平台已发布非遗档案 <b class="xl-num">{{ t0Projects.length }}</b> 项 ·
        代表性传承人 {{ person.name }}
      </p>
      <p v-else class="fallback-note" data-fallback-note>
        数据库非遗档案尚未发布 · 以上为离线兜底（客户材料）
      </p>

      <p class="heritage__foot">
        <a class="home-heritage__act xl-go" href="/heritage">
          进入传承档案
          <span class="home-heritage__act-arr xl-go__arr" aria-hidden="true">→</span>
        </a>
      </p>
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
