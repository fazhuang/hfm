<script setup lang="ts">
/**
 * HomeView — homepage 8-section orchestrator (CF-07).
 *
 * Thin orchestration layer ONLY. The accepted homepage macro sequence is
 * composed from eight presentation sections, each of which owns exactly one
 * stable section identity:
 *
 *   01 Hero → 02 一生 → 03 一部书 → 04 知识对象 → 05 史料证据
 *   → 06 活态传承 → 07 研究导航 → 08 Institutional Close
 *
 * SEARCH OWNERSHIP: HomeView owns the page-level search state + submit
 * (pushing to the real /search route). HomeHeroSection receives the state
 * and the handler as props (presentation component). No duplicate search
 * state and no second search implementation.
 *
 * FOOTER: the global semantic <footer> (AppFooter) belongs to PublicLayout.
 * HomeClosingSection is the homepage narrative close — it is not a second
 * footer and duplicates no footer responsibilities.
 *
 * DATA: every section reads the existing verified projection/data path
 * (homeProjection + config + inventory/search/heritage modules); CF-07 adds
 * only deterministic presentation projections. No new domain facts.
 */
import { ref } from 'vue'
import { useHomePublicData } from '../composables/useHomePublicData'
import { useRouter } from 'vue-router'
import HomeHeroSection from '../components/home/HomeHeroSection.vue'
import HomeLifeSection from '../components/home/HomeLifeSection.vue'
import HomeBookSection from '../components/home/HomeBookSection.vue'
import HomeKnowledgeSection from '../components/home/HomeKnowledgeSection.vue'
import HomeEvidenceSection from '../components/home/HomeEvidenceSection.vue'
import HomeHeritageSection from '../components/home/HomeHeritageSection.vue'
import HomeDomainsSection from '../components/home/HomeDomainsSection.vue'
import HomeClosingSection from '../components/home/HomeClosingSection.vue'

defineOptions({ name: 'HomeView' })

const router = useRouter()
const searchInput = ref('')
const { source: homeSource, enrichment: homeEnrichment } = useHomePublicData()

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
    />
    <HomeLifeSection />
    <HomeBookSection />
    <HomeKnowledgeSection />
    <HomeEvidenceSection />
    <HomeHeritageSection />
    <HomeDomainsSection :published="homeEnrichment" />
    <HomeClosingSection />
  </div>
</template>

<style scoped>
/* CF-08/09 geometry: the homepage is full-bleed (not clamped to
 * --hfm-content-max) so every section renders at the accepted 1272px artboard
 * geometry (inner column → 84px gutters; hero absolute coordinates land at the
 * frozen positions). Sections 01–04 (CF-08) and 05–08 (CF-09) each own their
 * content column; no global constraint is applied here. */
.home {
  display: block;
}
</style>
