<script setup lang="ts">
/**
 * HeritageView — CF-05 非遗活态传承档案（rebuild）。
 *
 * 继承已授权内容与 IA（KEEP_CONTENT_ONLY + REIMPLEMENT_PRESENTATION）：
 *   hero/项目 → 传承人物（刘君奇·第六代）→ 传承谱系（已确认节点 + PARTIAL）
 *     → 认定与荣誉 → 学术与技术成果 → 师承教育 → 工作室 → 媒体报道
 *     → 重要时间节点（chronology）→ 来源与证据 → 相关导航。
 *
 * Data source（CF-05 §5）：Recovery 无已发布 heritage API 记录，页面继续使用
 * 已版本化、已授权的 zzcl/ 审计注册静态内容（src/data/heritageView.ts）——
 * USE_VERSIONED_CONTENT = TRUE。不新增 API/DB/谱系节点/人物/师承关系。
 *
 * 谱系语义（CF-05 §7/§8）：仅已确认节点（皇甫谧 → 刘君奇·第六代）；中间代
 * 以正式 PARTIAL 数据状态表达（公开文案，不暴露 LINEAGE_STRUCTURING /
 * DATA-GAP / TODO 等内部治理术语）。PARTIAL ≠ ERROR ≠ COMPLETE ≠ 占位。
 *
 * CF-02（CF-05 §9）：stateMapping 提供谱系 PARTIAL 与人物已确认状态的标签
 * 与语义；不强行套用 DHObjectLayout / BibliographicRecord（本项目是活态档案
 * 多区段页面，非单一书目对象；强行使用会扭曲信息架构）。
 */
import { computed } from 'vue'
import {
  HERITAGE_ACADEMIC,
  HERITAGE_APPRENTICESHIPS,
  HERITAGE_LINEAGE,
  HERITAGE_MEDIA,
  HERITAGE_PERSON,
  HERITAGE_PROJECT,
  HERITAGE_RECOGNITIONS,
  HERITAGE_STUDIOS,
  HERITAGE_TECHNICAL,
  HERITAGE_TIMELINE,
} from '../../data/heritageView'
import { presentationStatusLabel } from '../../presentation/stateMapping'
import type { TimelineEvent } from '../../types/timeline'
import LineageGraph from '../../components/heritage/LineageGraph.vue'
import { mediaBytesUrl } from '../../services/media'
import { HERITAGE_COLLECTION } from '../../data/heritageCollection'
import Timeline from '../../components/Timeline.vue'

defineOptions({ name: 'HeritageView' })

/** 已陈列的件数（只含已发布者）。 */
const collectionTotal = HERITAGE_COLLECTION.reduce((n, g) => n + g.items.length, 0)

const heritageTimeline: TimelineEvent[] = HERITAGE_TIMELINE.map((t) => ({
  id: t.id,
  title: t.title,
  date: t.date,
}))

/** CF-02 label for the confirmed person node (generation is closed). */
const PERSON_NODE_STATE = presentationStatusLabel('COMPLETE', '传承节点已确认')

/** Distinct public source names actually referenced by this page's records. */
const recordSourceNames = computed<string[]>(() => {
  const seen = new Set<string>()
  const push = (name: string): void => {
    if (name !== undefined && name !== '') seen.add(name)
  }
  for (const rec of HERITAGE_RECOGNITIONS) push(rec.sourceName)
  for (const rec of HERITAGE_ACADEMIC) push(rec.sourceName)
  for (const rec of HERITAGE_TECHNICAL) push(rec.sourceName)
  for (const rec of HERITAGE_APPRENTICESHIPS) push(rec.sourceName)
  for (const rec of HERITAGE_STUDIOS) push(rec.sourceName)
  for (const rec of HERITAGE_MEDIA) push(rec.sourceName)
  return [...seen]
})
</script>

<template>
  <div class="heritage-page">
    <!-- 01 HERO — heritage identity/context (single coherent H1). -->
    <header class="heritage-hero">
      <p class="hfm-eyebrow">数字人文 · 非遗活态传承档案</p>
      <h1 class="heritage-hero__title">{{ HERITAGE_PROJECT.name }}非遗</h1>
      <p class="heritage-hero__person">
        <span class="heritage-hero__gen">{{ HERITAGE_PERSON.generationTitle }}</span>
        <span class="heritage-hero__name">{{ HERITAGE_PERSON.name }}</span>
      </p>
      <p class="heritage-hero__role">
        {{ HERITAGE_PERSON.heritageRole }} · {{ HERITAGE_PERSON.institutionRole }}
      </p>
      <p class="heritage-hero__note">
        本页为非遗活态传承数字档案：传承人物、认定与荣誉、学术与技术成果、师承教育、工作室、
        媒体报道与传承谱系。档案记录事实，不提供医疗建议。
      </p>
    </header>

    <!-- 02 非遗项目 — heritage project/context. -->
    <section class="heritage-section" aria-labelledby="project-heading" data-record-kind="project">
      <h2 id="project-heading" class="section-title">非遗项目</h2>
      <dl class="project-profile">
        <div class="project-profile__row">
          <dt>项目</dt>
          <dd>{{ HERITAGE_PROJECT.name }}</dd>
        </div>
        <div class="project-profile__row">
          <dt>分类</dt>
          <dd>{{ HERITAGE_PROJECT.classification }}</dd>
        </div>
        <div class="project-profile__row">
          <dt>认定</dt>
          <dd>{{ HERITAGE_PROJECT.recognitionLevel }}</dd>
        </div>
        <div class="project-profile__row">
          <dt>传承人</dt>
          <dd>{{ HERITAGE_PROJECT.inheritors.join('；') }}</dd>
        </div>
        <div class="project-profile__row">
          <dt>说明</dt>
          <dd>{{ HERITAGE_PROJECT.description }}</dd>
        </div>
      </dl>
      <p class="record-source">来源：{{ HERITAGE_PROJECT.sourceName }}</p>
    </section>

    <!-- 03 传承人物档案 — representative inheritor (刘君奇·第六代名医). -->
    <section
      id="profile"
      class="heritage-section"
      aria-labelledby="profile-heading"
      data-record-kind="person"
    >
      <h2 id="profile-heading" class="section-title">传承人物档案</h2>
      <article class="person-profile">
        <p class="person-profile__identity">
          <span class="person-profile__gen">{{ HERITAGE_PERSON.generationTitle }}</span>
          <span class="person-profile__name">{{ HERITAGE_PERSON.name }}</span>
          <span
            class="person-profile__state"
            data-status-prefix="presentation"
            data-status="COMPLETE"
            >{{ PERSON_NODE_STATE }}</span
          >
        </p>
        <p class="person-profile__role">{{ HERITAGE_PERSON.heritageRole }}</p>
        <p class="person-profile__title">{{ HERITAGE_PERSON.professionalTitle }}</p>
        <p class="person-profile__institution">{{ HERITAGE_PERSON.institutionRole }}</p>
        <p class="person-profile__bio">{{ HERITAGE_PERSON.biography }}</p>
        <div class="person-profile__roles">
          <h3 class="person-profile__sub">学术任职</h3>
          <ul>
            <li v-for="role in HERITAGE_PERSON.academicRoles" :key="role">{{ role }}</li>
          </ul>
        </div>
        <p class="person-profile__source">来源：{{ HERITAGE_PERSON.sourceName }}</p>
      </article>
    </section>

    <!-- 04 传承谱系 — confirmed nodes + explicit PARTIAL state. -->
    <section
      id="lineage"
      class="heritage-section"
      aria-labelledby="lineage-heading"
      data-record-kind="lineage"
    >
      <h2 id="lineage-heading" class="section-title">传承谱系</h2>
      <p class="section-note">
        本档案仅收录已确认的传承节点：皇甫谧（源头）→ 刘君奇（第六代名医）。第二代至第五代
        中间代资料尚未完整收录，当前仅掌握部分传承信息；平台不虚构人物或师承关系。
      </p>
      <LineageGraph :nodes="HERITAGE_LINEAGE" />
    </section>

    <!-- 05 认定与荣誉 -->
    <section class="heritage-section" aria-labelledby="recognition-heading">
      <h2 id="recognition-heading" class="section-title">认定与荣誉</h2>
      <p class="section-note">结构化记录（客户资料）；证书图像整理中，后续以脱敏公开副本呈现。</p>
      <ul class="record-list">
        <li v-for="rec in HERITAGE_RECOGNITIONS" :key="rec.id" class="record-card">
          <p class="record-card__title">{{ rec.title }}</p>
          <p class="record-card__meta">
            <span>{{ rec.category }}</span>
            <span v-if="rec.issuer !== '—'">{{ rec.issuer }}</span>
            <span v-if="rec.date !== '—'">{{ rec.date }}</span>
          </p>
          <p v-if="rec.description" class="record-card__desc">{{ rec.description }}</p>
          <p class="record-card__source">来源：{{ rec.sourceName }}</p>
        </li>
      </ul>
    </section>

    <!-- 06 学术与技术成果 -->
    <section class="heritage-section" aria-labelledby="achievements-heading">
      <h2 id="achievements-heading" class="section-title">学术与技术成果</h2>

      <h3 class="sub-title">学术成果</h3>
      <ul class="achievement-list">
        <li v-for="a in HERITAGE_ACADEMIC" :key="a.id" class="achievement-item">
          <p class="achievement-item__title">{{ a.title }}</p>
          <p class="achievement-item__meta">
            {{ a.type }}<template v-if="a.year !== '—'"> · {{ a.year }}</template>
            <template v-if="a.description"> · {{ a.description }}</template>
          </p>
        </li>
      </ul>

      <h3 class="sub-title">技术成果</h3>
      <ul class="achievement-list">
        <li v-for="t in HERITAGE_TECHNICAL" :key="t.id" class="achievement-item">
          <p class="achievement-item__title">{{ t.title }}</p>
          <p class="achievement-item__meta">
            {{ t.award }}<template v-if="t.year !== '—'"> · {{ t.year }}</template>
          </p>
          <p v-if="t.description" class="achievement-item__desc">{{ t.description }}</p>
        </li>
      </ul>
    </section>

    <!-- 07 师承教育 -->
    <section id="apprenticeship" class="heritage-section" aria-labelledby="apprenticeship-heading">
      <h2 id="apprenticeship-heading" class="section-title">师承教育</h2>
      <div class="event-list">
        <article v-for="event in HERITAGE_APPRENTICESHIPS" :key="event.id" class="event-card">
          <p class="event-card__title">{{ event.title }}</p>
          <p class="event-card__meta">
            {{ event.date }}<template v-if="event.location"> · {{ event.location }}</template>
          </p>
          <p class="event-card__desc">{{ event.description }}</p>
          <p class="event-card__source">来源：{{ event.sourceName }}</p>
        </article>
      </div>
    </section>

    <!-- 08 名中医工作室 -->
    <section id="studios" class="heritage-section" aria-labelledby="studios-heading">
      <h2 id="studios-heading" class="section-title">名中医工作室</h2>
      <ul class="record-list">
        <li v-for="studio in HERITAGE_STUDIOS" :key="studio.id" class="record-card">
          <p class="record-card__title">{{ studio.name }}</p>
          <p class="record-card__meta">{{ studio.institution }}</p>
          <p v-if="studio.description" class="record-card__desc">{{ studio.description }}</p>
          <p class="record-card__source">来源：{{ studio.sourceName }}</p>
        </li>
      </ul>
    </section>

    <!-- 09 媒体报道 -->
    <section id="media" class="heritage-section" aria-labelledby="media-heading">
      <h2 id="media-heading" class="section-title">媒体报道</h2>
      <ul class="record-list">
        <li v-for="m in HERITAGE_MEDIA" :key="m.id" class="record-card">
          <p class="record-card__title">{{ m.title }}</p>
          <p class="record-card__meta">
            {{ m.mediaOutlet }}<template v-if="m.date !== '—'"> · {{ m.date }}</template>
          </p>
          <p v-if="m.description" class="record-card__desc">{{ m.description }}</p>
          <p class="record-card__source">来源：{{ m.sourceName }}</p>
        </li>
      </ul>
    </section>

    <!-- 10 重要时间节点（chronology ≠ lineage） -->
    <section class="heritage-section" aria-labelledby="timeline-heading">
      <h2 id="timeline-heading" class="section-title">重要时间节点</h2>
      <p class="section-note">按年代排序（chronology）；时间顺序不代表师承关系。</p>
      <Timeline :events="heritageTimeline" label="非遗传承重要时间节点" />
    </section>

    <!-- 10b 成果陈列 — 非遗佐证的实物（P-6）。
         只列已发布的 28 件：P2/P3 仍在库中保持 draft，不在此列。
         封面由 PDF 首页渲染而来；原件自始至终未经改动。 -->
    <section id="collection" class="heritage-section" aria-labelledby="collection-heading">
      <h2 id="collection-heading" class="section-title">成果陈列</h2>
      <p class="section-note">
        客户提供的非遗佐证材料中已公开发布的部分，共
        {{ collectionTotal }} 件。点开即读原件 —— 这是传承的凭据本身，不是转述。
      </p>

      <div v-for="group in HERITAGE_COLLECTION" :key="group.category" class="collection-group">
        <h3 class="collection-group__title">{{ group.category }}</h3>
        <p class="collection-group__note">{{ group.note }}</p>
        <ul class="collection-grid">
          <li v-for="item in group.items" :key="item.id" class="collection-card">
            <a
              class="collection-card__link"
              :href="mediaBytesUrl(item.id)"
              target="_blank"
              rel="noopener"
            >
              <span class="collection-card__frame">
                <img
                  v-if="item.kind === 'pdf'"
                  :src="item.cover"
                  :alt="`${item.name} 首页`"
                  loading="lazy"
                />
                <span v-else class="collection-card__noimg">{{ item.kind.toUpperCase() }}</span>
              </span>
              <span class="collection-card__name">{{ item.name }}</span>
            </a>
          </li>
        </ul>
      </div>
    </section>

    <!-- 11 来源与证据 — public provenance labels only. -->
    <section class="heritage-section" aria-labelledby="evidence-heading">
      <h2 id="evidence-heading" class="section-title">来源与证据</h2>
      <p class="section-note">
        本页记录均来自客户提供材料，各条记录已注明公开来源名；详细证据链（Citation）在研究端逐步呈现。
        档案记录事实，不提供临床诊疗建议。
      </p>
      <ul class="source-list">
        <li v-for="name in recordSourceNames" :key="name">{{ name }}</li>
      </ul>
    </section>

    <!-- 12 Related -->
    <nav class="heritage-related" aria-label="相关导航">
      <a href="/persons/ENT-PERSON-HFM-HUANGFUMI">皇甫谧人物档案</a>
      <a href="/jiayi">《针灸甲乙经》</a>
      <a href="/yan">其言</a>
      <a href="/archive">数字档案</a>
      <a href="/search?q=刘君奇">检索：刘君奇</a>
    </nav>
  </div>
</template>

<style scoped>
.heritage-page {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.heritage-hero {
  padding: var(--hfm-space-8) 0 var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  margin-bottom: var(--hfm-space-12);
}

.heritage-hero__title {
  font-size: var(--hfm-text-3xl);
  margin: 0 0 var(--hfm-space-3);
  letter-spacing: var(--hfm-tracking-display);
}

.heritage-hero__person {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-3);
  margin: 0 0 var(--hfm-space-2);
}

.heritage-hero__gen {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-xl);
  color: var(--hfm-color-heritage);
  font-weight: 600;
}

.heritage-hero__name {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-2xl);
  font-weight: 600;
}

.heritage-hero__role {
  color: var(--hfm-color-text-secondary);
  margin: 0 0 var(--hfm-space-3);
  overflow-wrap: anywhere;
}

.heritage-hero__note {
  color: var(--hfm-color-text-muted);
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
  margin: 0;
}

.collection-group {
  margin-bottom: var(--hfm-space-8);
}
.collection-group__title {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  letter-spacing: 0.06em;
  color: var(--hfm-color-text);
}
.collection-group__note {
  margin: 0 0 var(--hfm-space-4);
  max-width: var(--hfm-reader-max);
  font-size: var(--hfm-text-sm);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-muted);
}
/* 陈列：统一画框、统一比例、统一留白 —— 这一段的成败在整齐，不在花哨。 */
.collection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
  gap: var(--hfm-space-4);
  margin: 0;
  padding: 0;
  list-style: none;
}
.collection-card__link {
  display: block;
  color: inherit;
  text-decoration: none;
}
.collection-card__frame {
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  background: var(--hfm-color-surface);
  border: 1px solid var(--hfm-color-border);
}
.collection-card__frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
}
.collection-card__noimg {
  font-family: var(--hfm-font-sans);
  font-size: var(--hfm-text-xs);
  letter-spacing: var(--hfm-tracking-display);
  color: var(--hfm-color-text-muted);
}
.collection-card__name {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: var(--hfm-space-2);
  font-size: var(--hfm-text-xs);
  line-height: var(--hfm-leading-normal);
  color: var(--hfm-color-text-secondary);
}
.collection-card__link:hover .collection-card__frame {
  border-color: var(--hfm-color-border-strong);
}
.collection-card__link:focus-visible {
  outline: 2px solid var(--hfm-color-interactive);
  outline-offset: 2px;
}

.heritage-section {
  margin-bottom: var(--hfm-space-12);
}

.section-title {
  margin: 0 0 var(--hfm-space-4);
  padding-bottom: var(--hfm-space-2);
  border-bottom: 1px solid var(--hfm-color-border);
}

.section-note {
  color: var(--hfm-color-text-muted);
  max-width: 68ch;
  margin: 0 0 var(--hfm-space-4);
  line-height: var(--hfm-leading-reading);
}

.sub-title {
  font-size: var(--hfm-text-lg);
  margin: var(--hfm-space-6) 0 var(--hfm-space-3);
}

/* dl grid helper — safe at 375px. */
.project-profile {
  margin: 0;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  overflow: hidden;
}

.project-profile__row {
  display: grid;
  grid-template-columns: minmax(4.5rem, 6rem) minmax(0, 1fr);
  gap: var(--hfm-space-4);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.project-profile__row:last-child {
  border-bottom: none;
}

.project-profile__row dt {
  color: var(--hfm-color-text-muted);
  font-weight: 600;
}

.project-profile__row dd {
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}

.record-source,
.record-card__source {
  margin: var(--hfm-space-2) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

/* person profile (representative inheritor). */
.person-profile {
  padding: var(--hfm-space-5) var(--hfm-space-6);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  display: grid;
  gap: var(--hfm-space-2);
}

.person-profile__identity {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--hfm-space-2) var(--hfm-space-3);
}

.person-profile__gen {
  color: var(--hfm-color-heritage);
  font-family: var(--hfm-font-serif);
  font-weight: 600;
  font-size: var(--hfm-text-lg);
}

.person-profile__name {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-2xl);
  font-weight: 600;
}

.person-profile__state {
  display: inline-block;
  padding: 2px var(--hfm-space-2);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-success-surface);
  color: var(--hfm-color-success);
  font-size: var(--hfm-text-xs);
  font-weight: 600;
}

.person-profile__role {
  margin: 0;
  font-weight: 600;
}

.person-profile__title,
.person-profile__institution,
.person-profile__bio {
  margin: 0;
  color: var(--hfm-color-text-secondary);
}

.person-profile__bio {
  line-height: var(--hfm-leading-reading);
}

.person-profile__roles {
  margin-top: var(--hfm-space-2);
}

.person-profile__sub {
  margin: 0 0 var(--hfm-space-2);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}

.person-profile__roles ul {
  margin: 0;
  padding-left: var(--hfm-space-4);
  display: grid;
  gap: var(--hfm-space-1);
}

.person-profile__source {
  margin: var(--hfm-space-2) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

/* generic record cards (recognition / studio / media). */
.record-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
}

.record-card {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.record-card__title {
  margin: 0 0 var(--hfm-space-1);
  font-weight: 600;
}

.record-card__meta {
  margin: 0 0 var(--hfm-space-1);
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-3);
}

.record-card__desc {
  margin: 0;
  color: var(--hfm-color-text-secondary);
  line-height: var(--hfm-leading-reading);
  font-size: var(--hfm-text-sm);
}

.record-card__source {
  margin-top: var(--hfm-space-2);
}

/* achievements. */
.achievement-list {
  list-style: none;
  margin: 0 0 var(--hfm-space-4);
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.achievement-item {
  padding: var(--hfm-space-2) 0;
  border-bottom: 1px solid var(--hfm-color-border);
}

.achievement-item__title {
  margin: 0;
  font-weight: 600;
}

.achievement-item__meta {
  margin: 2px 0 0;
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.achievement-item__desc {
  margin: 2px 0 0;
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

/* apprenticeship events. */
.event-list {
  display: grid;
  gap: var(--hfm-space-3);
}

.event-card {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.event-card__title {
  margin: 0 0 var(--hfm-space-1);
  font-weight: 600;
}

.event-card__meta {
  margin: 0 0 var(--hfm-space-1);
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.event-card__desc {
  margin: 0;
  line-height: var(--hfm-leading-reading);
}

.event-card__source {
  margin: var(--hfm-space-2) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

/* provenance source index. */
.source-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
}

.heritage-related {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-5);
  padding: var(--hfm-space-4) 0;
  border-top: 1px solid var(--hfm-color-border);
}

.heritage-related a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.heritage-related a:hover {
  text-decoration: underline;
}
</style>
