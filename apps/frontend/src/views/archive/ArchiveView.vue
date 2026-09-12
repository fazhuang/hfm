<script setup lang="ts">
/**
 * ArchiveView — 数字档案 (UI-06) 平台收录概览。
 *
 * 回答"平台收录了什么"（公共视角），不是后台文件系统。所有来源以可理解
 * 名称展示（sourceName），绝不渲染内部绝对文件路径。非遗详细展示属 UI-09，
 * 本页仅提供入口。
 */
import { ARCHIVE_GROUPS } from '../../data/archiveInventory'

defineOptions({ name: 'ArchiveView' })
</script>

<template>
  <section class="archive" aria-labelledby="archive-heading">
    <header class="archive-hero">
      <p class="hfm-eyebrow">数字人文 · 馆藏档案</p>
      <h1 id="archive-heading" class="archive-hero__title">数字档案</h1>
      <p class="archive-hero__intro">
        平台收录内容概览：皇甫谧人物资料、著作、版本资料、现代研究、影像与非遗资料。
        每条档案注明公开来源名称与收录状态。
      </p>
    </header>

    <section
      v-for="group in ARCHIVE_GROUPS"
      :key="group.category"
      class="archive-group"
      :aria-labelledby="`group-${group.category}-heading`"
    >
      <h2 :id="`group-${group.category}-heading`" class="section-title">
        {{ group.label }}
        <span class="section-title__desc">{{ group.description }}</span>
      </h2>

      <ul class="archive-list">
        <li v-for="record in group.records" :key="record.id" class="archive-item">
          <a v-if="record.href" :href="record.href" class="archive-item__link">
            <span class="archive-item__title">{{ record.title }}</span>
          </a>
          <span v-else class="archive-item__title">{{ record.title }}</span>

          <p class="archive-item__desc">{{ record.description }}</p>
          <p class="archive-item__meta">
            <span class="hfm-status" :data-status="record.status">
              {{
                record.status === 'AVAILABLE'
                  ? '已展示'
                  : record.status === 'METADATA_ONLY'
                    ? '元数据已录'
                    : '整理中'
              }}
            </span>
            <span v-if="record.count !== undefined" class="archive-item__count">
              {{ record.count }} 件（据客户材料审计）
            </span>
            <span class="archive-item__source">{{ record.sourceName }}</span>
          </p>
        </li>
      </ul>
    </section>

    <p class="archive-note">
      档案为数字化材料登记（可理解来源名称）；详细原文展示按内容准入进度逐步开放。
      非遗资料详细展示见<a class="archive-note__link" href="/heritage">皇甫谧针灸非遗传承</a>。
    </p>
  </section>
</template>

<style scoped>
.archive {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.archive-hero {
  padding: var(--hfm-space-8) 0 var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-12);
}

.archive-hero__title {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-3);
  letter-spacing: var(--hfm-tracking-display);
}

.archive-hero__intro {
  color: var(--hfm-color-text-secondary);
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
  margin: 0;
}

.archive-group {
  margin-bottom: var(--hfm-space-12);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.section-title__desc {
  display: block;
  margin-top: var(--hfm-space-1);
  font-size: var(--hfm-text-sm);
  font-weight: 400;
  color: var(--hfm-color-text-muted);
}

.archive-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.archive-item {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.archive-item__link {
  text-decoration: none;
  color: var(--hfm-color-text);
}

.archive-item__link:hover .archive-item__title {
  color: var(--hfm-color-accent);
}

.archive-item__title {
  font-weight: 600;
}

.archive-item__desc {
  margin: 0;
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
}

.archive-item__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
  align-items: center;
}

.archive-note {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.archive-note__link {
  color: var(--hfm-color-interactive);
}
</style>
