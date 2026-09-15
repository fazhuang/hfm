<script setup lang="ts">
/**
 * HomeView — 首页编排（HFM-UI-CONTRACT-v2 §3.1，参考图 `HFM-SY-CK.png`）。
 *
 * 六段：首屏 → 四入口带 → 皇甫谧与《针灸甲乙经》 → 数字人文视角 → 活态传承 → 收尾。
 * 内容分三层（契约 §4）：静态叙事层（`src/data/*.ts`）、受控资产层（公开媒体
 * 接口）、live 计数（公开接口，取不到就不显示）。
 *
 * 检索不在首页里 —— 它属于页头工具区，全站唯一（契约 §5.7）。
 */
import { computed } from 'vue'
import { HOME_DOMAINS } from '../data/homeProjection'
import { useHomeContractData } from '../composables/useHomeContractData'
import HomeHeroSection from '../components/home/HomeHeroSection.vue'
import HomeClassicsSection from '../components/home/HomeClassicsSection.vue'
import HomeApproachSection from '../components/home/HomeApproachSection.vue'
import HomeHeritageSection from '../components/home/HomeHeritageSection.vue'
import HomeClosingSection from '../components/home/HomeClosingSection.vue'

defineOptions({ name: 'HomeView' })

const { home, heritage } = useHomeContractData()

/** 后端计数是否真的到位；供排查用，不参与渲染。 */
const homeSource = computed(() => {
  const c = home.value.data?.counts
  const hasData = !!c && c.works + c.persons + c.c_terms + c.heritage_projects > 0
  return home.value.source === 'backend' && hasData ? 'backend' : 'fallback'
})
</script>

<template>
  <div class="home" :data-home-source="homeSource">
    <HomeHeroSection :block="home" />

    <!-- 段 02：四入口带（参考图 band 2）。 -->
    <nav id="home-entries" class="xl-entries home__entries" aria-label="主要探索入口">
      <a v-for="d in HOME_DOMAINS.domains" :key="d.no" class="xl-entry" :href="d.href">
        <svg class="xl-entry__mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
          <rect x="6" y="5" width="20" height="22" stroke="currentColor" stroke-width="1.2" />
          <path d="M11 11h10M11 16h10M11 21h6" stroke="currentColor" stroke-width="1.2" />
        </svg>
        <span class="xl-entry__en">{{ d.en }}</span>
        <p class="xl-entry__title">{{ d.title }}</p>
        <p class="xl-entry__note">{{ d.key }}</p>
        <span class="xl-entry__go">{{ d.cta }} →</span>
      </a>
    </nav>

    <HomeClassicsSection />
    <HomeApproachSection :block="home" />
    <HomeHeritageSection :block="heritage" />
    <HomeClosingSection />
  </div>
</template>

<style scoped>
.home {
  display: block;
}
</style>
