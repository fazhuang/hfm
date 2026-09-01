<script setup lang="ts">
/**
 * PersonDetailView — FLAGSHIP-01 Huangfu Mi Profile (UI-04).
 *
 * Digital Scholarly Biography 页面模型（UI-00 v2）：
 * Hero → 皇甫谧 215—282 → 权威人物定义 → 多维身份 → 生平（时间轴）→
 * 其传 → 其言精选 → 主要著作 → 《针灸甲乙经》 → 后论/历史评价 →
 * 电影/影像 → 相关史料（Evidence/Citation 可见）。
 *
 * Data policy: real data from the public person projection where available;
 * customer-confirmed flagship anchors (dates / definition / identities /
 * life phases / works entries) render for the core person from config until
 * content admission ([DATA-GAP: CONTENT_METADATA / ENTITY_RELATIONS]);
 * everything else degrades to graceful empty states — no fabricated content.
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ApiError, fetchPublicMedia, fetchPublicPerson } from '../../services/api'
import {
  formatBytes,
  isPlayableVideo,
  MEDIA_CATEGORY_LABELS,
  mediaBytesUrl,
} from '../../services/media'
import type { MediaAssetItem } from '../../types/media'
import type { PersonAssertion, PersonEvent, PublicPerson } from '../../types/public'
import type { TimelineEvent } from '../../types/timeline'
import {
  CORE_PERSON_DATES,
  CORE_PERSON_DEFINITION,
  CORE_PERSON_IDENTITIES,
  CORE_PERSON_LIFE_PHASES,
  CORE_PERSON_NAME,
  CORE_PERSON_WORKS,
} from '../../config/corePerson'
import Timeline from '../../components/Timeline.vue'
import EmptyState from '../../components/states/EmptyState.vue'
import ErrorState from '../../components/states/ErrorState.vue'
import LoadingState from '../../components/states/LoadingState.vue'

defineOptions({ name: 'PersonDetailView' })

const route = useRoute()
const person = ref<PublicPerson | null>(null)
const movies = ref<MediaAssetItem[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const isCorePerson = computed(() => person.value?.name_zh === CORE_PERSON_NAME)

const timelineEvents = computed<TimelineEvent[]>(() => {
  const apiEvents: TimelineEvent[] = (person.value?.events ?? []).map((e: PersonEvent) => ({
    id: e.event_id,
    title: e.role,
    description: e.description ?? undefined,
  }))
  // Core person: customer-confirmed life phases frame the (not-yet-admitted) data.
  if (isCorePerson.value && apiEvents.length === 0) {
    return CORE_PERSON_LIFE_PHASES.map((phase, i) => ({
      id: `phase-${i}`,
      title: phase.title,
      description: phase.note,
    }))
  }
  return apiEvents
})

const evidencedAssertions = computed<PersonAssertion[]>(() =>
  (person.value?.assertions ?? []).filter((a) => a.evidence_ids.length > 0),
)

onMounted(async () => {
  const entityId = String(route.params.id ?? '')
  try {
    person.value = await fetchPublicPerson(entityId)
    const media = await fetchPublicMedia('movie')
    movies.value = media.slice(0, 8)
  } catch (err) {
    error.value = err instanceof ApiError ? err.message : '人物资料加载失败。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="person" aria-labelledby="person-heading">
    <p class="person__back"><a class="back-link" href="/">← 返回首页</a></p>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="error" />
    <EmptyState v-else-if="person === null" label="人物不存在或未发布。" />

    <template v-else>
      <!-- Hero -->
      <header class="person-hero">
        <p class="person-hero__dates" v-if="isCorePerson">{{ CORE_PERSON_DATES }}</p>
        <h1 id="person-heading" class="person-hero__name">{{ person.name_zh || '未命名' }}</h1>
        <p class="person-hero__meta">
          {{ person.name_pinyin || '' }}
          <template v-if="person.courtesy_name"> · 字 {{ person.courtesy_name }}</template>
          <template v-if="person.pseudonym"> · 号 {{ person.pseudonym }}</template>
          <template v-if="person.dynasty"> · {{ person.dynasty }}</template>
        </p>
        <p v-if="isCorePerson" class="person-hero__definition">{{ CORE_PERSON_DEFINITION }}</p>
      </header>

      <!-- 多维身份 -->
      <section class="person-section" aria-labelledby="identities-heading">
        <h2 id="identities-heading" class="section-title">多维身份</h2>
        <ul v-if="isCorePerson" class="identity-tags" aria-label="多维身份">
          <li v-for="identity in CORE_PERSON_IDENTITIES" :key="identity" class="identity-tag">
            {{ identity }}
          </li>
        </ul>
        <EmptyState v-else label="身份信息整理中。" />
      </section>

      <!-- 生平 -->
      <section class="person-section" aria-labelledby="life-heading">
        <h2 id="life-heading" class="section-title">生平</h2>
        <Timeline
          v-if="timelineEvents.length > 0"
          :events="timelineEvents"
          label="皇甫谧生平时间轴"
        />
        <EmptyState v-else label="生平内容整理中。" />
      </section>

      <!-- 其传 -->
      <section class="person-section" aria-labelledby="biography-heading">
        <h2 id="biography-heading" class="section-title">其传</h2>
        <EmptyState label="其传全文整理中（客户资料：其传）。" />
      </section>

      <!-- 其言精选 -->
      <section class="person-section" aria-labelledby="qiyan-heading">
        <h2 id="qiyan-heading" class="section-title">其言精选</h2>
        <p class="section-note">
          三都赋、玄守论、释劝论、笃终论。全文见<a class="inline-link" href="/yan">其言</a>。
        </p>
        <EmptyState label="其言摘句整理中。" />
      </section>

      <!-- 主要著作 -->
      <section class="person-section" aria-labelledby="works-heading">
        <h2 id="works-heading" class="section-title">主要著作</h2>
        <ul v-if="isCorePerson" class="works-grid">
          <li v-for="work in CORE_PERSON_WORKS" :key="work.title" class="work-card">
            <a :href="work.href" class="work-card__link">
              <span class="work-card__title">{{ work.title }}</span>
              <span class="work-card__note">{{ work.note }}</span>
            </a>
          </li>
        </ul>
        <EmptyState v-else label="著作信息整理中。" />
      </section>

      <!-- 后论 / 历史评价 -->
      <section class="person-section" aria-labelledby="afterwords-heading">
        <h2 id="afterwords-heading" class="section-title">后论 / 历史评价</h2>
        <EmptyState label="历史评价整理中（客户资料：后论）。" />
      </section>

      <!-- 相关史料（Evidence 可见） -->
      <section class="person-section" aria-labelledby="evidence-heading">
        <h2 id="evidence-heading" class="section-title">史料依据</h2>
        <EmptyState v-if="evidencedAssertions.length === 0" label="史料断言整理中。" />
        <ul v-else class="assertion-list">
          <li v-for="assertion in evidencedAssertions" :key="assertion.id" class="assertion-item">
            <p class="assertion-item__value">{{ assertion.value }}</p>
            <p class="assertion-item__meta">
              <span class="assertion-item__predicate">{{ assertion.predicate }}</span>
              <span class="assertion-item__confidence">{{ assertion.confidence }}</span>
              <span class="evidence-badge" title="已绑定证据"
                >证据 ×{{ assertion.evidence_ids.length }}</span
              >
            </p>
          </li>
        </ul>
      </section>

      <!-- 电影 / 影像 -->
      <section class="person-section" aria-labelledby="media-heading">
        <h2 id="media-heading" class="section-title">影像资料</h2>
        <EmptyState v-if="movies.length === 0" label="暂无影像资料。" />
        <ul v-else class="movie-list">
          <li v-for="movie in movies" :key="movie.id" class="movie-card">
            <h3 class="movie-card__title">{{ movie.name }}</h3>
            <p class="movie-card__meta">
              {{ MEDIA_CATEGORY_LABELS[movie.category] }} · {{ formatBytes(movie.byte_size) }}
            </p>
            <p class="movie-card__rights">{{ movie.license_basis }}</p>
            <video
              v-if="isPlayableVideo(movie.mime_type)"
              :src="mediaBytesUrl(movie.id)"
              controls
              preload="none"
            />
            <p v-else>
              <a class="open-link" :href="mediaBytesUrl(movie.id)" target="_blank" rel="noopener"
                >打开</a
              >
            </p>
          </li>
        </ul>
      </section>

      <p class="person__evidence-note">
        本页史实均以版本与证据为准：来源、版本与 Citation 将在内容准入后逐条呈现。
      </p>
    </template>
  </section>
</template>

<style scoped>
.person {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.person__back {
  margin: 0 0 var(--hfm-space-4);
}

.back-link {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.person-hero {
  padding: var(--hfm-space-8) 0 var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-8);
}

.person-hero__dates {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-numeric);
  font-variant-numeric: tabular-nums;
  color: var(--hfm-color-heritage);
  letter-spacing: 0.1em;
}

.person-hero__name {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-3);
  letter-spacing: var(--hfm-tracking-display);
}

.person-hero__meta {
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-4);
}

.person-hero__definition {
  max-width: 60ch;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  line-height: var(--hfm-leading-reading);
  color: var(--hfm-color-text);
  margin: 0;
}

.person-section {
  margin-bottom: var(--hfm-space-12);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.section-note {
  color: var(--hfm-color-text-muted);
  margin: 0 0 var(--hfm-space-3);
}

.inline-link {
  color: var(--hfm-color-interactive);
}

.identity-tags {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
}

.identity-tag {
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-border-strong);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.works-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--hfm-space-3);
}

.work-card {
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.work-card__link {
  display: flex;
  flex-direction: column;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-4);
  text-decoration: none;
  color: var(--hfm-color-text);
}

.work-card__link:hover .work-card__title {
  color: var(--hfm-color-accent);
}

.work-card__title {
  font-family: var(--hfm-font-serif);
  font-weight: 600;
}

.work-card__note {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.assertion-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.assertion-item {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.assertion-item__value {
  margin: 0 0 var(--hfm-space-2);
  line-height: var(--hfm-leading-reading);
}

.assertion-item__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2);
  align-items: center;
  margin: 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.assertion-item__predicate {
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-canvas);
}

.evidence-badge {
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-success-surface);
  color: var(--hfm-color-success);
  font-weight: 600;
}

.movie-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-4);
}

.movie-card {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.movie-card__title {
  margin: 0 0 var(--hfm-space-1);
}

.movie-card__meta {
  margin: 0 0 var(--hfm-space-1);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

.movie-card__rights {
  margin: 0 0 var(--hfm-space-2);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-xs);
}

.movie-card video {
  width: 100%;
  max-height: 420px;
  background: var(--hfm-color-canvas);
  border-radius: var(--hfm-radius-sm);
}

.open-link {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-weight: 600;
}

.person__evidence-note {
  margin-top: var(--hfm-space-8);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}
</style>
