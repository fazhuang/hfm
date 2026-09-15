<script setup lang="ts">
/**
 * HomeClosingSection — 首页段 06「收尾」（契约 v2 §3.1 段 06）。
 *
 * 参考图 `HFM-SY-CK.png` 的收尾是一整幅风景影像压暗，上面一层大字引文，
 * 右侧 `HFM` 圆形标记与两句短语。
 *
 * **底图没有做**：我们没有可用的风景照片，拿一张无关的图顶上比留黑更糟
 * （契约 §5.6）。这里用最深的暗带承担同一件事 —— 引文、标记、题词都在。
 */
import { HOME_CLOSING } from '../../data/homeProjection'

defineOptions({ name: 'HomeClosingSection' })
</script>

<template>
  <section id="home-closing" class="xl-sec xl-sec--close close" aria-labelledby="close-quote">
    <div class="xl-inner">
      <div class="close__grid">
        <div class="close__quote-block">
          <p id="close-quote" class="close__quote">{{ HOME_CLOSING.quote }}</p>
          <p class="close__quote-en">{{ HOME_CLOSING.quoteEn }}</p>
        </div>

        <div class="close__mark-block">
          <p class="close__mark" aria-hidden="true">HFM</p>
          <p class="close__motto">
            <span v-for="m in HOME_CLOSING.motto" :key="m">{{ m }}</span>
          </p>
        </div>
      </div>

      <div class="close__foot">
        <p class="close__name">{{ HOME_CLOSING.name }}</p>
        <a class="close__cta xl-cta" :href="HOME_CLOSING.cta.href">
          {{ HOME_CLOSING.cta.label }}
          <span class="xl-cta__arr" aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.close {
  background: var(--wl-deep);
}
.close__grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: clamp(2rem, 4vw, 3rem);
  align-items: center;
}
@media (min-width: 900px) {
  .close__grid {
    grid-template-columns: minmax(0, 1fr) auto;
  }
}

.close__quote {
  margin: 0;
  max-width: 30ch;
  font-family: var(--hfm-font-serif);
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  line-height: 1.85;
  color: #f2f0ea;
}
.close__quote-en {
  margin: var(--hfm-space-4) 0 0;
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.26em;
  font-size: 0.625rem;
  color: rgba(239, 237, 230, 0.5);
}

.close__mark-block {
  display: flex;
  align-items: center;
  gap: var(--hfm-space-5);
}
.close__mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 5.5rem;
  height: 5.5rem;
  margin: 0;
  font-family: var(--wl-latin);
  letter-spacing: 0.12em;
  font-size: var(--hfm-text-sm);
  color: rgba(220, 171, 116, 0.9);
  border: 1px solid rgba(220, 171, 116, 0.45);
  border-radius: 50%;
  user-select: none;
}
.close__motto {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  letter-spacing: 0.12em;
  color: rgba(239, 237, 230, 0.8);
}

.close__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--hfm-space-4);
  margin-top: clamp(2.5rem, 5vw, 3.5rem);
  padding-top: var(--hfm-space-5);
  border-top: 1px solid rgba(239, 237, 230, 0.14);
}
.close__name {
  margin: 0;
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-lg);
  letter-spacing: 0.14em;
  color: rgba(239, 237, 230, 0.72);
}
.close__cta {
  display: inline-flex;
  align-items: center;
  gap: var(--hfm-space-2);
  padding: 0.6rem 1.3rem;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.06em;
  color: #f2f0ea;
  text-decoration: none;
  border: 1px solid rgba(239, 237, 230, 0.24);
  border-radius: 2px;
}
.close__cta:hover {
  border-color: var(--wl-mark);
  color: var(--wl-mark-strong);
}
.close__cta:focus-visible {
  outline: 2px solid var(--wl-mark);
  outline-offset: 3px;
}
</style>
