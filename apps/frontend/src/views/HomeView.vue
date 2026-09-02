<script setup lang="ts">
/**
 * HomeView — UI-03 flagship homepage, STEP 3 WP-02 structural shell.
 *
 * Thin orchestrator for the accepted 8-section production structure:
 *   Hero → Life → Book → Knowledge → Evidence → Heritage → Domains → Closing.
 *
 * SECTION OWNERSHIP (accepted baseline HFM_HOMEPAGE_STEP2_VISUAL_BASELINE_FINAL):
 *   each Home*Section owns exactly one accepted section. This view only
 *   composes them in the accepted order and owns page-level search state.
 *
 * FOOTER: the global <footer> is AppFooter, rendered by PublicLayout (it wraps
 * <main><RouterView/></main>). Required behavior / search capability survives.
 * The homepage search interface is owned here (page-level state + submit),
 * and passed to HomeHeroSection as the visible search interface; no duplicate
 * SEARCH_INDEX or search logic lives in the hero. (PublicLayout separately owns
 * a general header-search; both push to /search as before.)
 *
 * DATA: all content comes from homeProjection / corePerson / presentation
 * mappings (additive projections introduced for the 8-section structure).
 * No duplicated authoritative literals, no fabricated counts.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import HomeHeroSection from '../components/home/HomeHeroSection.vue'
import HomeLifeSection from '../components/home/HomeLifeSection.vue'
import HomeBookSection from '../components/home/HomeBookSection.vue'
import HomeKnowledgeSection from '../components/home/HomeKnowledgeSection.vue'
import HomeEvidenceSection from '../components/home/HomeEvidenceSection.vue'
import HomeHeritageSection from '../components/home/HomeHeritageSection.vue'
import HomeDomainsSection from '../components/home/HomeDomainsSection.vue'
import HomeClosingSection from '../components/home/HomeClosingSection.vue'

/* Note on data-status (UX2-P5 P1-01): the shared P0 G1-C presentation-state
 * mapping (resolvePresentationState / presentationStatusLabel) is owned by the
 * sections that DISPLAY a data-status — HomeBookSection (版本关系整理中) and
 * HomeHeritageSection (谱系整理中). It is not duplicated here at the
 * orchestrator level. The section roots carry the / data-status values. */

defineOptions({ name: 'HomeView' })

const router = useRouter()
const searchInput = ref('')

function onSearch(): void {
  const q = searchInput.value.trim()
  void router.push({ path: '/search', query: q ? { q } : {} })
}
</script>

<template>
  <div class="home">
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
    <HomeDomainsSection />
    <HomeClosingSection />
  </div>
</template>

<style scoped>
/* WP-02 structural shell only — no final section visuals. The accepted
   8-section composition is implemented in later WPs; this is the orchestration
   spine + minimal flow/rhythm. */
.home {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
