<script setup lang="ts">
/**
 * ReaderDocView — UI-07 Ancient Text / Scholarly Reader.
 *
 * Professional long-text reading: reading typography (.hfm-reading based),
 * section navigation (URL-hash recoverable), citation blocks, source/edition
 * aside, related entities, font-size controls, invalid-id state. All text is
 * real customer content; classical full texts absent from materials stay
 * METADATA_ONLY (clear status, never fabricated).
 */
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  getReaderDocument,
  READER_DOCUMENTS,
  READER_METADATA_ONLY,
} from '../../data/readerDocuments'
import type { ReaderDocument } from '../../types/reader'
import CitationBlock from '../../components/reader/CitationBlock.vue'

defineOptions({ name: 'ReaderDocView' })

const route = useRoute()
const docId = computed(() => String(route?.params?.id ?? ''))
const document = computed<ReaderDocument | undefined>(() => getReaderDocument(docId.value))

const activeSection = ref('')
watch(
  () => route?.hash,
  () => {
    activeSection.value = (route?.hash ?? '').replace('#', '')
  },
  { immediate: true },
)

const fontScale = ref(1)
function adjustFont(delta: number): void {
  fontScale.value = Math.min(1.25, Math.max(0.875, fontScale.value + delta))
}

const readingFontSize = computed(() => `${fontScale.value}em`)
</script>

<template>
  <article class="reader" aria-labelledby="reader-title">
    <!-- Invalid / missing document -->
    <section v-if="!document" class="reader__not-found" aria-labelledby="reader-notfound-heading">
      <h1 id="reader-notfound-heading" class="reader__notfound-title">未找到该文献</h1>
      <p>所请求的文献不存在或尚未收录。</p>
      <p class="reader__notfound-links">
        <a href="/works">论著与研究</a>
        ·
        <a href="/archive">数字档案</a>
        ·
        <a href="/search">检索</a>
      </p>
    </section>

    <template v-else>
      <!-- Header -->
      <header class="reader__header">
        <p class="reader__text-type">{{ document.textType }}</p>
        <h1 id="reader-title" class="reader__title">{{ document.title }}</h1>
        <p class="reader__subtitle">{{ document.subtitle }}</p>
        <p class="reader__meta">
          <span v-if="document.attribution">整理：{{ document.attribution }}</span>
          <span v-if="document.period">时期：{{ document.period }}</span>
          <span class="reader__status">{{
            document.readingStatus === 'FULL_TEXT' ? '全文可读' : document.readingStatus
          }}</span>
        </p>
      </header>

      <!-- Font controls -->
      <div class="reader__controls" aria-label="字号">
        <button type="button" aria-label="减小字号" @click="adjustFont(-0.125)">A−</button>
        <button type="button" aria-label="恢复标准字号" @click="adjustFont(1 - fontScale)">
          标准
        </button>
        <button type="button" aria-label="增大字号" @click="adjustFont(0.125)">A＋</button>
      </div>

      <!-- METADATA_ONLY state (classical full texts) -->
      <section
        v-if="document.readingStatus === 'METADATA_ONLY'"
        class="reader__metadata-only"
        role="status"
        aria-labelledby="metadata-only-heading"
      >
        <h2 id="metadata-only-heading">当前仅有题录</h2>
        <p>{{ document.description }}</p>
        <p>古典全文整理中；整理说明见<a href="/yan">其言</a>。</p>
      </section>

      <template v-else>
        <div class="reader__layout">
          <!-- Section navigation -->
          <nav v-if="document.sections.length > 1" class="reader__nav" aria-label="章节导航">
            <a
              v-for="section in document.sections"
              :key="section.id"
              class="reader__nav-item"
              :class="{ 'reader__nav-item--active': activeSection === section.id }"
              :href="`#${section.id}`"
            >
              {{ section.heading }}
            </a>
          </nav>

          <!-- Reading pane -->
          <div class="reader__pane">
            <section
              v-for="section in document.sections"
              :id="section.id"
              :key="section.id"
              class="reader__section"
              :aria-labelledby="`${section.id}-heading`"
            >
              <h2 :id="`${section.id}-heading`" class="reader__section-heading">
                {{ section.heading }}
              </h2>

              <!-- Paragraphs with citations -->
              <template v-if="section.paragraphs">
                <p
                  v-for="paragraph in section.paragraphs"
                  :id="`${section.id}-${paragraph.id}`"
                  :key="paragraph.id"
                  class="reader__paragraph hfm-reading"
                  :style="{ fontSize: readingFontSize }"
                >
                  {{ paragraph.text }}
                </p>
                <CitationBlock
                  v-for="paragraph in section.paragraphs.filter((p) => p.citation)"
                  :key="`citation-${paragraph.id}`"
                  :title="document.title"
                  :attribution="paragraph.citation?.attribution"
                  :work="document.title"
                  :section="section.heading"
                  :source="paragraph.citation?.source ?? document.source"
                >
                  {{ paragraph.text }}
                </CitationBlock>
              </template>

              <!-- Table-like entries -->
              <ul v-else-if="section.entries" class="reader__entries">
                <li v-for="(entry, i) in section.entries" :key="i" class="reader__entry">
                  <p class="reader__entry-title">{{ entry.title }}</p>
                  <p v-if="entry.meta" class="reader__entry-meta">{{ entry.meta }}</p>
                  <p v-if="entry.note" class="reader__entry-note">{{ entry.note }}</p>
                </li>
              </ul>
            </section>

            <!-- Footer navigation -->
            <nav class="reader__footer-nav" aria-label="阅读底部导航">
              <a href="/works">论著与研究</a>
              <a href="/archive">数字档案</a>
              <a href="/search">检索</a>
            </nav>
          </div>

          <!-- Aside: source / edition / evidence / related -->
          <aside class="reader__aside" aria-label="文献信息">
            <h2 class="reader__aside-title">文献信息</h2>
            <dl class="reader__aside-list">
              <div class="reader__aside-row">
                <dt>来源</dt>
                <dd>{{ document.source }}</dd>
              </div>
              <div class="reader__aside-row">
                <dt>内容状态</dt>
                <dd>{{ document.readingStatus }}</dd>
              </div>
              <div v-if="document.editionContext" class="reader__aside-row">
                <dt>版本</dt>
                <dd>
                  {{ document.editionContext.work }}
                  <template v-if="document.editionContext.edition">
                    · {{ document.editionContext.edition }}</template
                  >
                </dd>
              </div>
            </dl>
            <h2 class="reader__aside-title">相关</h2>
            <ul class="reader__aside-related">
              <li v-for="entity in document.relatedEntities" :key="entity.href">
                <a :href="entity.href">{{ entity.label }}</a>
              </li>
            </ul>
          </aside>
        </div>
      </template>

      <!-- Other reader documents -->
      <nav class="reader__documents" aria-label="其他文献">
        <h2 class="reader__documents-title">平台文献</h2>
        <ul>
          <li v-for="doc in READER_DOCUMENTS" :key="doc.id">
            <a :href="`/reader/${doc.id}`">{{ doc.title }}</a>
            <span class="reader__documents-status">{{ doc.readingStatus }}</span>
          </li>
          <li v-for="entry in READER_METADATA_ONLY" :key="entry.id">
            {{ entry.title }}
            <span class="reader__documents-status">仅题录</span>
            <a href="/yan">（整理说明见其言）</a>
          </li>
        </ul>
      </nav>
    </template>
  </article>
</template>

<style scoped>
.reader {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.reader__header {
  padding: var(--hfm-space-6) 0 var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-5);
}

.reader__title {
  font-size: var(--hfm-text-2xl);
  margin: 0 0 var(--hfm-space-2);
  letter-spacing: var(--hfm-tracking-display);
}

.reader__subtitle {
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-2);
}

.reader__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-5);
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.reader__status {
  color: var(--hfm-color-success);
  font-weight: 600;
}

.reader__controls {
  display: flex;
  gap: var(--hfm-space-2);
  margin-bottom: var(--hfm-space-4);
}

.reader__controls button {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
  cursor: pointer;
  font-size: var(--hfm-text-sm);
}

.reader__metadata-only {
  padding: var(--hfm-space-8) var(--hfm-space-5);
  border: 1px dashed var(--hfm-color-border-strong);
  border-radius: var(--hfm-radius-md);
  color: var(--hfm-color-text-secondary);
}

.reader__metadata-only h2 {
  margin-top: 0;
  color: var(--hfm-color-warning);
}

.reader__layout {
  display: grid;
  grid-template-columns: 12rem minmax(0, 1fr) 14rem;
  gap: var(--hfm-space-6);
  align-items: start;
}

.reader__nav {
  position: sticky;
  top: var(--hfm-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
}

.reader__nav-item {
  padding: var(--hfm-space-1) var(--hfm-space-2);
  border-left: 3px solid transparent;
  color: var(--hfm-color-text-secondary);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
  scroll-margin-top: var(--hfm-space-8);
}

.reader__nav-item:hover {
  color: var(--hfm-color-text);
}

.reader__nav-item--active {
  border-left-color: var(--hfm-color-accent);
  color: var(--hfm-color-accent);
  font-weight: 600;
}

.reader__section {
  scroll-margin-top: var(--hfm-space-8);
  margin-bottom: var(--hfm-space-8);
}

.reader__section-heading {
  margin: 0 0 var(--hfm-space-3);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.reader__paragraph {
  margin: 0 0 var(--hfm-space-4);
}

.reader__entries {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.reader__entry {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.reader__entry-title {
  margin: 0;
  font-weight: 600;
}

.reader__entry-meta {
  margin: 0;
  color: var(--hfm-color-heritage);
  font-size: var(--hfm-text-xs);
}

.reader__entry-note {
  margin: 0;
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
}

.reader__footer-nav {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4);
  margin-top: var(--hfm-space-8);
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--hfm-color-border);
}

.reader__footer-nav a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.reader__aside {
  position: sticky;
  top: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  padding: var(--hfm-space-4);
}

.reader__aside-title {
  font-size: var(--hfm-text-sm);
  margin: 0 0 var(--hfm-space-2);
  color: var(--hfm-color-text-muted);
}

.reader__aside-title + .reader__aside-title {
  margin-top: var(--hfm-space-5);
}

.reader__aside-list {
  margin: 0;
}

.reader__aside-row {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-1) 0;
  font-size: var(--hfm-text-sm);
}

.reader__aside-row dt {
  color: var(--hfm-color-text-muted);
  font-weight: 600;
  font-size: var(--hfm-text-xs);
}

.reader__aside-row dd {
  margin: 0;
  color: var(--hfm-color-text-secondary);
}

.reader__aside-related {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.reader__aside-related a {
  color: var(--hfm-color-interactive);
  font-size: var(--hfm-text-sm);
  text-decoration: none;
}

.reader__aside-related a:hover {
  text-decoration: underline;
}

.reader__not-found {
  padding: var(--hfm-space-12) var(--hfm-space-6);
  text-align: center;
}

.reader__notfound-links a {
  color: var(--hfm-color-interactive);
}

.reader__documents {
  margin-top: var(--hfm-space-10);
  border-top: 1px solid var(--hfm-color-border);
  padding-top: var(--hfm-space-4);
}

.reader__documents-title {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.reader__documents ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.reader__documents li {
  display: flex;
  gap: var(--hfm-space-3);
  align-items: baseline;
  font-size: var(--hfm-text-sm);
}

.reader__documents a {
  color: var(--hfm-color-interactive);
}

.reader__documents-status {
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-xs);
}

@media (max-width: 1023px) {
  .reader__layout {
    grid-template-columns: 1fr;
  }

  .reader__nav,
  .reader__aside {
    position: static;
  }

  .reader__nav {
    flex-direction: row;
    flex-wrap: wrap;
    border-bottom: 1px solid var(--hfm-color-border);
    padding-bottom: var(--hfm-space-2);
  }

  .reader__nav-item {
    border-left: none;
    border-bottom: 2px solid transparent;
  }

  .reader__nav-item--active {
    border-bottom-color: var(--hfm-color-accent);
  }
}
</style>
