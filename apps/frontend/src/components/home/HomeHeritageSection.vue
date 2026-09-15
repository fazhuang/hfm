<script setup lang="ts">
/**
 * HomeHeritageSection — 首页段 05「活态传承 · 连接当下」（契约 v2 §3.1 段 05）。
 *
 * 参考图 `HFM-SY-CK.png` 的这一段是：三张实景卡 + 右侧引文 + CTA。
 * 三张卡用的是客户提供的真实照片，说明压在图上。
 * 已发布非遗档案的总数由一行真实投影承载（契约 §5.6：取不到就不写，不显示 0）。
 */
import { computed } from 'vue'
import { HOME_HERITAGE_LIVING, HOME_LIVING } from '../../data/homeProjection'
import type { BlockData } from '../../composables/useHomeContractData'

defineOptions({ name: 'HomeHeritageSection' })

const props = defineProps<{ block?: BlockData<unknown[]> | null }>()

const person = HOME_HERITAGE_LIVING.person

/** T0 — published heritage projects; empty until C1 publishes them (contract §6). */
const t0Projects = computed(() =>
  props.block?.source === 'backend' ? (props.block.data ?? []) : [],
)
const hasT0 = computed(() => t0Projects.value.length > 0)
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
          <span class="xl-label">{{ HOME_LIVING.en }}</span>
        </div>
        <div>
          <h2 id="home-heritage-title" class="xl-title">{{ HOME_LIVING.title }}</h2>
          <p class="xl-lede">{{ HOME_LIVING.lede }}</p>
        </div>
      </header>

      <div class="liv">
        <ul class="xl-cards">
          <li>
            <a class="xl-card" href="/heritage">
              <img
                src="/assets/heritage/heritage-baishi-ceremony.jpg"
                alt="皇甫谧学院师承教育拜师大会现场"
              />
              <span class="xl-card__caption">
                <span class="xl-card__en">Intangible Heritage</span>
                <span class="xl-card__title">非遗传承</span>
                <span class="xl-card__note">皇甫谧针灸 · 市级非遗代表性项目</span>
              </span>
            </a>
          </li>
          <li>
            <a class="xl-card" href="/heritage">
              <img
                src="/assets/heritage/01a099de-6383-75b4-8932-3fb563a12d78.jpg"
                alt="非遗佐证材料：央视《魅力中国城》栏目参与证明"
              />
              <span class="xl-card__caption">
                <span class="xl-card__en">Education</span>
                <span class="xl-card__title">教育教学</span>
                <span class="xl-card__note">师承带教与课堂现场 · 客户提供</span>
              </span>
            </a>
          </li>
          <li>
            <a class="xl-card" href="/jiayi">
              <img
                src="/assets/jiayi/book-siku-leaf.jpg"
                alt="四库全书本《针灸甲乙经》书叶"
              />
              <span class="xl-card__caption">
                <span class="xl-card__en">Local Culture</span>
                <span class="xl-card__title">地域文化</span>
                <span class="xl-card__note">灵台：皇甫谧故里 · 典籍版本</span>
              </span>
            </a>
          </li>
        </ul>

        <aside class="liv__aside">
          <p class="liv__quote">{{ HOME_LIVING.quote }}</p>
          <a class="liv__cta xl-cta" :href="HOME_LIVING.cta.href">
            {{ HOME_LIVING.cta.label }}
            <span class="xl-cta__arr" aria-hidden="true">→</span>
          </a>
          <p v-if="hasT0" class="liv__total">
            平台已发布非遗档案 <b class="xl-num">{{ t0Projects.length }}</b> 项 ·
            代表性传承人 {{ person.name }}
          </p>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ---- 段 05：三张卡 + 右侧引文 ---- */
.liv {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: clamp(2rem, 4vw, 3rem);
  align-items: start;
}
@media (min-width: 1000px) {
  .liv {
    grid-template-columns: minmax(0, 2.6fr) minmax(0, 1fr);
  }
}
.liv .xl-cards {
  grid-template-columns: minmax(0, 1fr);
}
@media (min-width: 700px) {
  .liv .xl-cards {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.liv__aside {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--hfm-space-5);
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
}
.liv__quote {
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  line-height: 1.95;
  color: var(--wl-ink);
}
/* 按钮外观来自 styles/home-scale.css 的 .xl-cta。 */
.liv__total {
  margin: 0;
  font-size: var(--hfm-text-xs);
  line-height: 1.8;
  color: var(--wl-mute);
}
.liv__total b {
  color: var(--wl-mark);
}

</style>
