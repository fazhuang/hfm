<script setup lang="ts">
/**
 * HomeHeroSection — homepage Section 01 (Hero H3).
 *
 * CF-07 STRUCTURAL SHELL ONLY. Semantic <section id="home-hero"> root with the
 * single page-level H1 (platform name) and the homepage search interface
 * boundary. Search STATE stays in HomeView (page-level owner); this section is
 * props/events presentation only (#home-search-input browser contract kept).
 * No final visual fidelity (no artwork heights / specimen assets / fixed
 * geometry) — that belongs to the visual work packages.
 *
 * DATA: identity / subtitle / definition from HOME_HERO + corePerson
 * projection (existing verified data; nothing new).
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
    <p class="hfm-eyebrow">
      <span class="home-chapter__no">{{ HOME_CHAPTERS.hero.no }}</span
      >{{ HOME_CHAPTERS.hero.label }}
    </p>
    <h1 id="home-hero-title" class="home-hero__title">
      {{ HOME_HERO.title }}
    </h1>
    <p class="home-hero__subtitle">
      {{ HOME_HERO.subtitle }}
    </p>
    <p class="home-hero__person">{{ name }} {{ dates }}</p>
    <p class="home-hero__definition">
      {{ HOME_HERO.definition }}
    </p>

    <div class="home-hero__actions">
      <a
        v-for="action in HOME_HERO.primary"
        :key="action.href"
        class="home-cta"
        :href="action.href"
        >{{ action.label }}</a
      >
      <a
        v-for="action in HOME_HERO.secondary"
        :key="action.href"
        class="home-cta home-cta--ghost"
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
        placeholder="检索人物、作品、版本、文献与论文…"
        @input="emit('update:searchValue', ($event.target as HTMLInputElement).value)"
      />
      <button class="home-search__submit" type="submit">检索</button>
    </form>
  </section>
</template>

<style scoped>
/* CF-07 STRUCTURAL SHELL ONLY — section boundary + basic flow. */
.home-chapter__no {
  margin-right: 0.6em;
  color: var(--hfm-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.home-section--hero {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
}

.home-hero__title {
  margin: var(--hfm-space-2) 0 var(--hfm-space-3);
}

.home-hero__subtitle,
.home-hero__person,
.home-hero__definition {
  color: var(--hfm-color-text-secondary);
  margin-bottom: var(--hfm-space-2);
}

.home-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin: var(--hfm-space-5) 0 0;
}

.home-cta {
  display: inline-block;
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  color: var(--hfm-color-on-accent);
  background: var(--hfm-color-accent);
  font-weight: 600;
  text-decoration: none;
}

.home-cta--ghost {
  background: transparent;
  color: var(--hfm-color-accent);
}

.home-search {
  display: flex;
  gap: var(--hfm-space-2);
  max-width: 32rem;
  margin-top: var(--hfm-space-4);
}

.home-search__input {
  flex: 1;
  min-width: 0;
  padding: var(--hfm-space-2) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
}

.home-search__submit {
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
  font-weight: 600;
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
