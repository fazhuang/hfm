<script setup lang="ts">
/**
 * HomeYanSection — contract §4 block 03 (其言).
 *
 * T0: NONE — the four texts are not content-admitted yet (§5 C4). The block
 * therefore renders an HONEST un-admitted state (contract §2 R3) over the
 * customer-material metadata projection; it never fabricates full text.
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
          <p class="xl-lede">三都赋序 · 玄守论 · 释劝论 · 笃终论</p>
        </div>
      </header>

      <p class="yan__state" data-empty-state>四篇全文尚未内容准入 · 以下为题录信息</p>

      <ul class="yan__items xl-rows">
        <li v-for="(item, i) in YAN_COLLECTION.sections" :key="item.id" class="xl-row yan__item">
          <span class="xl-row__index">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="xl-row__body yan__item-body">
            <span class="yan__item-title">{{ item.title }}</span>
            <span class="yan__item-meta">{{ YAN_COLLECTION.subtitle }}</span>
          </div>
        </li>
      </ul>

      <p class="yan__foot">
        <a class="home-yan__act xl-go" href="/yan">
          进入其言区 <span class="home-yan__act-arr xl-go__arr" aria-hidden="true">→</span>
        </a>
      </p>
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
