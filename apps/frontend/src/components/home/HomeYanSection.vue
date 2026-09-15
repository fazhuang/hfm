<script setup lang="ts">
/**
 * HomeYanSection — contract §4 block 03 (其言).
 *
 * T0: NONE — the four texts are not content-admitted. P-8a (2026-09-15)
 * entered them from public-domain editions, so full text now exists on /yan
 * as STATIC editorial content (data-source="static" there), which is a
 * different thing from an admitted backend projection. This block keeps
 * saying the honest thing (contract §2 R3): the texts are readable, and they
 * are not admitted. It previously read「尚未内容准入」while no text existed
 * anywhere, which made it true then and false after P-8a.
 */
import { YAN_COLLECTION } from '../../data/yanCollection'

defineOptions({ name: 'HomeYanSection' })
</script>

<template>
  <section id="home-yan" class="xl-sec" aria-labelledby="home-yan-title" data-source="fallback">
    <div class="xl-inner">
      <header class="xl-head">
        <div class="xl-head__aside">
          <span class="xl-index">03</span>
          <span class="xl-label">His Words</span>
        </div>
        <div>
          <h2 id="home-yan-title" class="xl-title">其言</h2>
          <!-- data-empty-state 是契约要求的如实状态标记：这一段不是从后端
               取来的投影，必须自己说清楚它的来源，不能让人误以为是 T0。 -->
          <p class="xl-lede" data-empty-state>
            四篇全文已依公版文献录入，可在其言页逐篇阅读。
          </p>
        </div>
      </header>

      <!-- 本段只做一件事：让他自己说一句。
           此前是一行为主干、外加说明与链接三件，等于把其言页搬了过来。 -->
      <div class="yan__quote-wrap">
        <blockquote class="yan__quote">
          人之所至惜者，命也；道之所必全者，形也；性形所不可犯者，疾病也。
          <cite>《玄守论》</cite>
        </blockquote>

        <p class="yan__titles">
          <span v-for="(item, i) in YAN_COLLECTION.sections" :key="item.id" class="yan__title">
            {{ item.title }}<template v-if="i < YAN_COLLECTION.sections.length - 1"> · </template>
          </span>
        </p>

        <p class="yan__foot">
          <a class="home-yan__act xl-go" href="/yan">
            进入其言区
            <span class="home-yan__act-arr xl-go__arr" aria-hidden="true">→</span>
          </a>
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.yan__state {
  margin: 0 0 var(--hfm-space-5);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-left: 2px solid var(--wl-mark);
  background: var(--wl-light);
  font-family: var(--wl-latin);
  font-size: var(--hfm-text-xs);
  letter-spacing: 0.06em;
  color: var(--wl-mark);
}
.yan__item-body {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--hfm-space-4);
  flex-wrap: wrap;
}
.yan__item-title {
  font-family: var(--hfm-font-heading);
  font-size: var(--hfm-text-xl);
  color: var(--wl-ink);
}
.yan__item-meta {
  font-size: var(--hfm-text-xs);
  color: var(--wl-mute);
}
.yan__foot {
  margin: var(--hfm-space-6) 0 0;
}
</style>

<style scoped>
/* 本段只放一句他自己的话 —— 元素少了，就该给足尺度和留白。 */
.yan__quote-wrap {
  max-width: 46rem;
}
.yan__quote {
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-size: clamp(1.25rem, 2.4vw, 1.75rem);
  line-height: 2;
  color: var(--wl-ink);
}
.yan__quote cite {
  display: block;
  margin-top: var(--hfm-space-4);
  font-style: normal;
  font-size: var(--hfm-text-sm);
  letter-spacing: 0.1em;
  color: var(--wl-mute);
}
.yan__titles {
  margin: var(--hfm-space-8) 0 0;
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--wl-rule);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  letter-spacing: 0.08em;
  color: var(--wl-ink-2);
}
.yan__foot {
  margin: var(--hfm-space-6) 0 0;
}
</style>
