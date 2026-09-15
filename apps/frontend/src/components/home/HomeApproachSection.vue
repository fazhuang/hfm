<script setup lang="ts">
/**
 * HomeApproachSection — 首页段 04「数字人文视角下的皇甫谧」（契约 v2 §3.1 段 04）。
 *
 * 左：标题 + 英文小标 + 一段正文 + CTA。右：四个数字指标。
 * 四个数字**全部来自已发布投影** `/api/v1/public/home` 的真实计数；
 * 取不到就不渲染这一段，不显示 0、不编造（契约 §5.6）。
 */
import { computed } from 'vue'
import { HOME_APPROACH } from '../../data/homeProjection'
import type { BlockData } from '../../composables/useHomeContractData'
import type { HomeProjection } from '../../types/public'

defineOptions({ name: 'HomeApproachSection' })

const props = defineProps<{ block?: BlockData<HomeProjection> | null }>()

interface Metric {
  key: string
  value: number
  zh: string
  note: string
}
interface Icon {
  key: string
  paths: string[]
}

const METRICS: readonly Metric[] = [
  { key: 'works', value: 0, zh: '已发布著作', note: '经内容准入并发布的著作' },
  { key: 'persons', value: 0, zh: '已发布人物', note: '与皇甫谧相关的历史人物' },
  { key: 'c_terms', value: 0, zh: '知识实体', note: '经穴、经脉、病症与治法术语' },
  { key: 'heritage_projects', value: 0, zh: '非遗档案', note: '皇甫谧针灸活态传承材料' },
]

const stats = computed(() => {
  const c = props.block?.data?.counts
  if (!c || props.block?.source !== 'backend') return null
  if (c.works + c.persons + c.c_terms + c.heritage_projects <= 0) return null
  return METRICS.map((m) => ({ ...m, value: Number(c[m.key as keyof typeof c] ?? 0) }))
})

/** 四个细线图标：书 / 人 / 网络 / 档案。 */
const ICONS: readonly Icon[] = [
  { key: 'works', paths: ['M6 5h20v22H6z', 'M11 11h10M11 16h10M11 21h6'] },
  { key: 'persons', paths: ['M16 15a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z', 'M6 27c0-5 4.5-8 10-8s10 3 10 8'] },
  { key: 'c_terms', paths: ['M16 6v20', 'M6 16h20', 'M9 9l14 14', 'M23 9L9 23'] },
  {
    key: 'heritage_projects',
    paths: ['M5 8h22v18H5z', 'M5 14h22', 'M12 8v18'],
  },
]
const iconFor = (key: string): Icon => ICONS.find((i) => i.key === key) ?? ICONS[0]
</script>

<template>
  <section v-if="stats" id="home-approach" class="xl-sec" aria-labelledby="home-approach-title">
    <div class="xl-inner">
      <div class="ap">
        <div class="ap__text">
          <h2 id="home-approach-title" class="ap__title">{{ HOME_APPROACH.title }}</h2>
          <p class="ap__en">{{ HOME_APPROACH.en }}</p>
          <p class="ap__body">{{ HOME_APPROACH.body }}</p>
          <a class="ap__cta xl-cta" :href="HOME_APPROACH.cta.href">
            {{ HOME_APPROACH.cta.label }}
            <span class="xl-cta__arr" aria-hidden="true">→</span>
          </a>
        </div>

        <ul class="ap__stats">
          <li v-for="s in stats" :key="s.key" class="ap__stat">
            <svg class="ap__icon" viewBox="0 0 32 32" fill="none" aria-hidden="true">
              <path
                v-for="d in iconFor(s.key).paths"
                :key="d"
                :d="d"
                stroke="currentColor"
                stroke-width="1.2"
              />
            </svg>
            <p class="ap__value">{{ s.value }}</p>
            <p class="ap__label">{{ s.zh }}</p>
            <p class="ap__note">{{ s.note }}</p>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ap {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: clamp(2rem, 4vw, 3.5rem);
  align-items: start;
}
@media (min-width: 1000px) {
  .ap {
    grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  }
}

.ap__title {
  margin: 0;
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: clamp(1.6rem, 3.4vw, 2.4rem);
  line-height: 1.35;
  color: var(--wl-ink);
}
.ap__en {
  margin: var(--hfm-space-3) 0 0;
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.26em;
  font-size: 0.625rem;
  color: var(--wl-mute);
}
.ap__body {
  margin: var(--hfm-space-5) 0 0;
  max-width: 40ch;
  font-size: var(--hfm-text-base);
  line-height: 2;
  color: var(--wl-ink-2);
}
/* 按钮外观来自 styles/home-scale.css 的 .xl-cta，这里只补本段的间距。 */
.ap__cta {
  margin-top: clamp(1.5rem, 3vw, 2rem);
}

.ap__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--hfm-space-8) var(--hfm-space-6);
  margin: 0;
  padding: 0;
  list-style: none;
}
@media (min-width: 700px) {
  .ap__stats {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
.ap__stat {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
}
.ap__icon {
  width: 1.75rem;
  height: 1.75rem;
  margin-bottom: var(--hfm-space-3);
  color: var(--wl-mark);
}
.ap__value {
  margin: 0;
  font-family: var(--wl-latin);
  font-variant-numeric: tabular-nums;
  font-size: clamp(1.75rem, 3.2vw, 2.5rem);
  line-height: 1;
  color: var(--wl-ink);
}
.ap__label {
  margin: 0;
  font-size: var(--hfm-text-base);
  color: var(--wl-ink);
}
.ap__note {
  margin: var(--hfm-space-2) 0 0;
  font-size: var(--hfm-text-xs);
  line-height: 1.75;
  color: var(--wl-mute);
}
</style>
