<script setup lang="ts">
/**
 * XlScaleBand — 《刻度带》 the homepage signature motif.
 *
 * Twenty ticks whose NORMALISED HEIGHT follows the digit-pair sequence read
 * from the inspiration string: 22,65,15,03,49,32,90,65,63,73,85,42,84,54,76,
 * 01,47,79,18,42 (0–100). The two extremes of the source — 01 (densest ink)
 * and 90 (lightest) — set the tonal range; the irregular spacing is the
 * source's own breath rhythm (gaps 1,13,5,7,14,11,2,4,26,11,4,5,1,11,22,…).
 *
 * Purely decorative (aria-hidden): a derived instrument mark, never data.
 */
defineProps<{ vertical?: boolean }>()

const STEPS = [22, 65, 15, 3, 49, 32, 90, 65, 63, 73, 85, 42, 84, 54, 76, 1, 47, 79, 18, 42]
//: The source's digit-gap rhythm, used as the inter-tick spacing.
const GAPS = [1, 13, 5, 7, 14, 11, 2, 4, 26, 11, 4, 5, 1, 11, 22, 3, 4, 8, 3, 4]
</script>

<template>
  <div class="band" :class="{ 'band--v': vertical }" aria-hidden="true">
    <span
      v-for="(value, i) in STEPS"
      :key="i"
      class="band__tick"
      :style="{ '--h': `${Math.max(8, value)}%`, '--g': `${(GAPS[i] ?? 4) * 0.5}px` }"
    />
  </div>
</template>

<style scoped>
.band {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 3.5rem;
}
.band__tick {
  flex: 1 1 0;
  min-width: 1px;
  height: var(--h);
  margin-left: var(--g);
  background: currentColor;
  opacity: calc(0.18 + (var(--h) / 100) * 0.82);
}
.band__tick:first-child {
  margin-left: 0;
}
.band--v {
  flex-direction: column;
  align-items: stretch;
  height: auto;
  width: 3.5rem;
}
.band--v .band__tick {
  width: var(--h);
  height: auto;
  min-height: 1px;
  flex: 1 1 0;
  margin-left: 0;
  margin-top: var(--g);
}
.band--v .band__tick:first-child {
  margin-top: 0;
}
</style>
