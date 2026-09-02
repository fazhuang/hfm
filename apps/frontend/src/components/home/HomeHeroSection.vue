<script setup lang="ts">
/**
 * HomeHeroSection — accepted homepage Section 01 (Hero H3 Refined).
 *
 * WP-02A STRUCTURAL SHELL ONLY. This is the clean WP-02 structural candidate:
 * semantic hero root + the one page-level H1 + the search interface boundary.
 * NO final visual treatment (no artwork heights, no manuscript specimen asset,
 * no grain/halo, no fixed artboard geometry) — that belongs to WP-03/03C.
 * Identity/subtitle/meta from the additive homeProjection + corePerson projection.
 */
import { HOME_HERO, HOME_CHAPTERS } from '../../data/homeProjection'
import { CORE_PERSON_NAME, CORE_PERSON_DATES } from '../../config/corePerson'

defineOptions({ name: 'HomeHeroSection' })

interface Props {
  searchValue?: string
  onSearch?: () => void
  searchLabel?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'update:searchValue', value: string): void }>()

const name = CORE_PERSON_NAME
const dates = CORE_PERSON_DATES
</script>

<template>
  <section id="home-hero" class="home-section home-section--hero" aria-labelledby="home-hero-title">
    <p class="home-eyebrow">
      <span class="home-eyebrow__no">{{ HOME_CHAPTERS.hero.no }}</span
      >{{ HOME_CHAPTERS.hero.label }}
    </p>
    <h1 id="home-hero-title" class="home-hero__title">{{ HOME_HERO.title }}</h1>
    <p class="home-hero__subtitle">{{ HOME_HERO.subtitle }}</p>
    <p class="home-hero__person">{{ name }} {{ dates }}</p>
    <p class="home-hero__definition">{{ HOME_HERO.definition }}</p>

    <div class="home-hero__actions">
      <a
        v-for="action in HOME_HERO.primary"
        :key="action.href"
        class="home-cta"
        :href="action.href"
        >{{ action.label }}</a
      >
    </div>

    <form
      v-if="searchLabel"
      class="home-search"
      role="search"
      :aria-label="searchLabel"
      @submit.prevent="props.onSearch"
    >
      <label class="visually-hidden" for="home-search-input">检索平台内容</label>
      <input
        id="home-search-input"
        :value="props.searchValue"
        class="home-search__input"
        type="search"
        placeholder="检索平台内容"
        @input="emit('update:searchValue', ($event.target as HTMLInputElement).value)"
      />
      <button class="home-search__submit" type="submit">检索</button>
    </form>
  </section>
</template>

<style scoped>
/* WP-02A STRUCTURAL SHELL ONLY — no final visual fidelity. */
.home-section--hero {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}
.home-hero__title {
  font-family: var(--hfm-font-display);
  margin: var(--hfm-space-3) 0;
}
.home-hero__person,
.home-hero__definition {
  color: var(--hfm-color-text-secondary);
}
.home-hero__actions {
  display: flex;
  gap: var(--hfm-space-4);
  margin: var(--hfm-space-5) 0;
}
.home-search {
  display: flex;
  gap: var(--hfm-space-2);
  max-width: 32rem;
}
.home-search__input {
  flex: 1;
}
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
