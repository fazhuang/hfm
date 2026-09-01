<script setup lang="ts">
/**
 * WorksView — 论著 / 研究 (UI-06) WORK 层作品目录。
 *
 * 语义分层：WORK（作品）≠ EDITION（版本，见 UI-08）≠ ARCHIVE RECORD（档案）。
 * 作品信息来自客户材料审计（论著目录 + 其言 docx）；字段缺失不显示，不以
 * "未知/N/A"堆积公共页面。
 */
import { WORK_COLLECTION } from '../../data/workCollection'
import { INVENTORY_LUNWEN_FILES, INVENTORY_LUNZHU_FILES } from '../../data/contentInventory'

defineOptions({ name: 'WorksView' })
</script>

<template>
  <section class="works" aria-labelledby="works-heading">
    <header class="works-hero">
      <p class="hfm-eyebrow">数字人文 · 论著与研究</p>
      <h1 id="works-heading" class="works-hero__title">论著 / 研究</h1>
      <p class="works-hero__intro">
        皇甫谧著作与相关研究的作品目录。按「作品 — 版本 — 档案」分层：
        作品为著作本身，版本为历代刊刻整理，档案为平台保存的数字化材料。
      </p>
    </header>

    <section class="works-section" aria-labelledby="collection-heading">
      <h2 id="collection-heading" class="section-title">作品目录</h2>
      <ul class="work-collection">
        <li v-for="work in WORK_COLLECTION" :key="work.id" class="work-entry">
          <a v-if="work.href" :href="work.href" class="work-entry__link">
            <span class="work-entry__title">{{ work.title }}</span>
            <span class="work-entry__meta">{{ work.historicalPeriod }} · {{ work.workType }}</span>
          </a>
          <template v-else>
            <span class="work-entry__title">{{ work.title }}</span>
            <span class="work-entry__meta">{{ work.historicalPeriod }} · {{ work.workType }}</span>
          </template>
          <p class="work-entry__desc">{{ work.description }}</p>
          <p class="work-entry__attr">
            <span>撰：{{ work.attribution }}</span>
            <span v-if="work.editionCount !== undefined">版本：{{ work.editionCount }} 种</span>
            <span v-if="work.note">{{ work.note }}</span>
          </p>
        </li>
      </ul>
    </section>

    <section class="works-section" aria-labelledby="register-heading">
      <h2 id="register-heading" class="section-title">材料规模</h2>
      <p class="works-register">
        据客户材料审计：论著资料 {{ INVENTORY_LUNZHU_FILES }} 件、学术论文
        {{ INVENTORY_LUNWEN_FILES }} 篇。题录与全文检索整理中。
      </p>
      <p class="works-cta">
        <a class="works-cta__link" href="/search?q=针灸甲乙经">检索全部文献 →</a>
        <a class="works-cta__link" href="/archive">数字档案 →</a>
      </p>
    </section>
  </section>
</template>

<style scoped>
.works {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.works-hero {
  padding: var(--hfm-space-8) 0 var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-12);
}

.works-hero__title {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-3);
  letter-spacing: var(--hfm-tracking-display);
}

.works-hero__intro {
  color: var(--hfm-color-text-secondary);
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
  margin: 0;
}

.works-section {
  margin-bottom: var(--hfm-space-12);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.work-collection {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.work-entry {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-4) var(--hfm-space-5);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.work-entry__link {
  display: grid;
  gap: var(--hfm-space-1);
  text-decoration: none;
  color: var(--hfm-color-text);
}

.work-entry__link:hover .work-entry__title {
  color: var(--hfm-color-accent);
}

.work-entry__title {
  font-family: var(--hfm-font-serif);
  font-weight: 600;
  font-size: var(--hfm-text-lg);
}

.work-entry__meta {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-heritage);
}

.work-entry__desc {
  margin: var(--hfm-space-1) 0 0;
  color: var(--hfm-color-text-secondary);
  line-height: var(--hfm-leading-normal);
  max-width: 68ch;
}

.work-entry__attr {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  margin: var(--hfm-space-1) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.works-register {
  color: var(--hfm-color-text-secondary);
  max-width: 68ch;
}

.works-cta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-5);
}

.works-cta__link {
  color: var(--hfm-color-interactive);
  font-weight: 600;
  text-decoration: none;
}

.works-cta__link:hover {
  text-decoration: underline;
}
</style>
