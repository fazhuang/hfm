<script setup lang="ts">
/**
 * HomeView — homepage orchestrator under HFM-FRONTEND-CONTENT-CONTRACT v1 §4.
 *
 * The homepage is the customer 5-link navigation's entry surface: five content
 * blocks (人物 / 其言 / 《针灸甲乙经》 / 非遗传承) plus a hero and an
 * institutional close. Every block binds to a T0 published projection and
 * degrades to a labelled T1 customer-material fallback when T0 is unavailable
 * (contract §2 R1–R3, §3).
 *
 * SEARCH OWNERSHIP: HomeView owns the page-level search state + submit
 * (→ the real /search route). The hero receives state + handler as props; the
 * single #home-search-input contract is preserved.
 */
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { HOME_DOMAINS } from '../data/homeProjection'
import { useHomeContractData } from '../composables/useHomeContractData'
import HomeHeroSection from '../components/home/HomeHeroSection.vue'
import HomePersonSection from '../components/home/HomePersonSection.vue'
import HomeYanSection from '../components/home/HomeYanSection.vue'
import HomeBookSection from '../components/home/HomeBookSection.vue'
import HomeHeritageSection from '../components/home/HomeHeritageSection.vue'
import HomeClosingSection from '../components/home/HomeClosingSection.vue'

defineOptions({ name: 'HomeView' })

const router = useRouter()
const searchInput = ref('')
const { home, person, work, editions, heritage } = useHomeContractData()

/** Page-level source marker: 'backend' iff the hero renders real T0 counts. */
const homeSource = computed(() => {
  const c = home.value.data?.counts
  const hasData = !!c && c.works + c.persons + c.c_terms + c.heritage_projects > 0
  return home.value.source === 'backend' && hasData ? 'backend' : 'fallback'
})

function onSearch(): void {
  const q = searchInput.value.trim()
  void router.push({ path: '/search', query: q ? { q } : {} })
}
</script>

<template>
  <div class="home" :data-home-source="homeSource">
    <HomeHeroSection
      v-model:search-value="searchInput"
      :on-search="onSearch"
      search-label="平台内容检索"
      :block="home"
    />
    <!-- 四入口带：契约 §4.2 规定它属于次屏，不在首屏之内。 -->
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
    <HomePersonSection :block="person" />
    <HomeYanSection />
    <HomeBookSection :work="work" :editions="editions" />
    <HomeHeritageSection :block="heritage" />
    <HomeClosingSection />
  </div>
</template>

<style scoped>
.home {
  display: block;
}
</style>
