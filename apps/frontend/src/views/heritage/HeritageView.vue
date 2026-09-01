<script setup lang="ts">
/**
 * HeritageView — FLAGSHIP-03 皇甫谧针灸非遗传承 (UI-09).
 *
 * LIVING HERITAGE SCHOLARLY ARCHIVE（非遗活态传承数字档案）。
 * 结构：非遗项目 → 第六代名医·刘君奇 → 认定与荣誉 → 学术与技术成果 →
 * 师承教育 → 名中医工作室 → 媒体报道 → 传承谱系 → 重要时间节点 → 证据。
 *
 * 数据均来自客户 zzcl/ 审计注册表；敏感字段（电话/证件/签字/名单）不进入
 * 公共派生。谱系仅已确认节点（皇甫谧 → … → 刘君奇·第六代），中间代
 * LINEAGE_STRUCTURING: PARTIAL，不虚构人物或师承边。chronology ≠ lineage。
 * 保持文化传承/历史档案语境，不提供任何医疗建议。
 */
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
import type { TimelineEvent } from '../../types/timeline'
import LineageGraph from '../../components/heritage/LineageGraph.vue'
import Timeline from '../../components/Timeline.vue'

defineOptions({ name: 'HeritageView' })

const heritageTimeline: TimelineEvent[] = HERITAGE_TIMELINE.map((t) => ({
  id: t.id,
  title: t.title,
  date: t.date,
}))
</script>

<template>
  <section class="heritage" aria-labelledby="heritage-heading">
    <!-- 01 Hero -->
    <header class="heritage-hero">
      <p class="hfm-eyebrow">数字人文 · 非遗活态传承档案</p>
      <h1 id="heritage-heading" class="heritage-hero__title">{{ HERITAGE_PROJECT.name }}非遗</h1>
      <div class="heritage-hero__person">
        <span class="heritage-hero__gen">第六代名医</span>
        <span class="heritage-hero__name">刘君奇</span>
      </div>
      <p class="heritage-hero__role">
        {{ HERITAGE_PERSON.heritageRole }} · {{ HERITAGE_PERSON.institutionRole }}
      </p>
      <p class="heritage-hero__note">
        本页为非遗活态传承数字档案：传承人物、认定与荣誉、学术与技术成果、师承教育、工作室、媒体报道与谱系。
        档案记录事实，不提供医疗建议。
      </p>
    </header>

    <!-- 02 非遗项目 -->
    <section class="heritage-section" aria-labelledby="project-heading">
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
    </section>

    <!-- 03 传承人物档案 -->
    <section id="profile" class="heritage-section" aria-labelledby="profile-heading">
      <h2 id="profile-heading" class="section-title">传承人物档案</h2>
      <article class="person-profile">
        <p class="person-profile__identity">
          <span class="person-profile__gen">{{ HERITAGE_PERSON.generationTitle }}</span>
          <span class="person-profile__name">{{ HERITAGE_PERSON.name }}</span>
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

    <!-- 04 认定与荣誉 -->
    <section class="heritage-section" aria-labelledby="recognition-heading">
      <h2 id="recognition-heading" class="section-title">认定与荣誉</h2>
      <p class="section-note">结构化记录（客户资料）；证书图像整理中，后续以脱敏公开副本呈现。</p>
      <ul class="recognition-list">
        <li v-for="rec in HERITAGE_RECOGNITIONS" :key="rec.id" class="recognition-item">
          <p class="recognition-item__title">{{ rec.title }}</p>
          <p class="recognition-item__meta">
            <span>{{ rec.category }}</span>
            <span v-if="rec.issuer !== '—'">{{ rec.issuer }}</span>
            <span v-if="rec.date !== '—'">{{ rec.date }}</span>
          </p>
          <p v-if="rec.description" class="recognition-item__desc">{{ rec.description }}</p>
        </li>
      </ul>
    </section>

    <!-- 05 学术与技术成果 -->
    <section class="heritage-section" aria-labelledby="achievements-heading">
      <h2 id="achievements-heading" class="section-title">学术与技术成果</h2>

      <h3 class="sub-title">学术成果</h3>
      <ul class="achievement-list">
        <li v-for="a in HERITAGE_ACADEMIC" :key="a.id" class="achievement-item">
          <span class="achievement-item__title">{{ a.title }}</span>
          <span class="achievement-item__meta"
            >{{ a.type }}<template v-if="a.year !== '—'"> · {{ a.year }}</template></span
          >
        </li>
      </ul>

      <h3 class="sub-title">技术成果</h3>
      <ul class="achievement-list">
        <li v-for="t in HERITAGE_TECHNICAL" :key="t.id" class="achievement-item">
          <span class="achievement-item__title">{{ t.title }}</span>
          <span class="achievement-item__meta"
            >{{ t.award }}<template v-if="t.year !== '—'"> · {{ t.year }}</template></span
          >
          <span v-if="t.description" class="achievement-item__desc">{{ t.description }}</span>
        </li>
      </ul>
    </section>

    <!-- 06 师承教育 -->
    <section id="apprenticeship" class="heritage-section" aria-labelledby="apprenticeship-heading">
      <h2 id="apprenticeship-heading" class="section-title">师承教育</h2>
      <article v-for="event in HERITAGE_APPRENTICESHIPS" :key="event.id" class="event-card">
        <p class="event-card__title">{{ event.title }}</p>
        <p class="event-card__meta">
          {{ event.date }}<template v-if="event.location"> · {{ event.location }}</template>
        </p>
        <p class="event-card__desc">{{ event.description }}</p>
        <p class="event-card__source">来源：{{ event.sourceName }}</p>
      </article>
    </section>

    <!-- 07 名中医工作室 -->
    <section id="studios" class="heritage-section" aria-labelledby="studios-heading">
      <h2 id="studios-heading" class="section-title">名中医工作室</h2>
      <ul class="studio-list">
        <li v-for="studio in HERITAGE_STUDIOS" :key="studio.id" class="studio-item">
          <p class="studio-item__name">{{ studio.name }}</p>
          <p class="studio-item__institution">{{ studio.institution }}</p>
          <p class="studio-item__desc">{{ studio.description }}</p>
        </li>
      </ul>
    </section>

    <!-- 08 媒体报道 -->
    <section id="media" class="heritage-section" aria-labelledby="media-heading">
      <h2 id="media-heading" class="section-title">媒体报道</h2>
      <ul class="media-list">
        <li v-for="m in HERITAGE_MEDIA" :key="m.id" class="media-item">
          <p class="media-item__title">{{ m.title }}</p>
          <p class="media-item__meta">
            {{ m.mediaOutlet }}<template v-if="m.date !== '—'"> · {{ m.date }}</template>
          </p>
          <p class="media-item__desc">{{ m.description }}</p>
        </li>
      </ul>
    </section>

    <!-- 09 传承谱系 -->
    <section class="heritage-section" aria-labelledby="lineage-heading">
      <h2 id="lineage-heading" class="section-title">传承谱系</h2>
      <p class="section-note">
        仅展示已确认节点：皇甫谧（源头）→ 刘君奇（第六代名医）。第二代至第五代谱系结构化整理中
        （LINEAGE_STRUCTURING: PARTIAL），不虚构人物或师承关系。
      </p>
      <LineageGraph :nodes="HERITAGE_LINEAGE" />
    </section>

    <!-- 10 重要时间节点（chronology ≠ lineage） -->
    <section class="heritage-section" aria-labelledby="timeline-heading">
      <h2 id="timeline-heading" class="section-title">重要时间节点</h2>
      <p class="section-note">按年代排序（chronology）；时间顺序不代表师承关系。</p>
      <Timeline :events="heritageTimeline" label="非遗传承重要时间节点" />
    </section>

    <!-- 11 Evidence -->
    <section class="heritage-section" aria-labelledby="evidence-heading">
      <h2 id="evidence-heading" class="section-title">来源与证据</h2>
      <p class="evidence-note">
        本页全部记录来自客户提供材料（zzcl 非遗传承申报档案），各条记录已注明公开来源名；
        详细证据链（Citation）在研究端逐步呈现。档案记录事实，不提供临床诊疗建议。
      </p>
    </section>

    <!-- Related -->
    <nav class="heritage-related" aria-label="相关导航">
      <a href="/persons/person-huangfu-mi">皇甫谧人物档案</a>
      <a href="/jiayi">《针灸甲乙经》</a>
      <a href="/yan">其言</a>
      <a href="/archive">数字档案</a>
      <a href="/search?q=刘君奇">检索：刘君奇</a>
    </nav>
  </section>
</template>

<style scoped>
.heritage {
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
  align-items: baseline;
  gap: var(--hfm-space-3);
  margin-bottom: var(--hfm-space-2);
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
}

.heritage-hero__note {
  color: var(--hfm-color-text-muted);
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
  margin: 0;
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
}

.sub-title {
  font-size: var(--hfm-text-lg);
  margin: var(--hfm-space-6) 0 var(--hfm-space-3);
}

.project-profile {
  margin: 0;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  overflow: hidden;
}

.project-profile__row {
  display: grid;
  grid-template-columns: 5rem 1fr;
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
  line-height: var(--hfm-leading-normal);
}

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
  align-items: baseline;
  gap: var(--hfm-space-3);
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

.person-profile__role {
  margin: 0;
  font-weight: 600;
}

.person-profile__title,
.person-profile__institution {
  margin: 0;
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
}

.person-profile__bio {
  margin: var(--hfm-space-1) 0 0;
  line-height: var(--hfm-leading-reading);
  max-width: 68ch;
}

.person-profile__sub {
  font-size: var(--hfm-text-base);
  margin: var(--hfm-space-2) 0 var(--hfm-space-1);
}

.person-profile__roles ul {
  margin: 0;
  padding-left: var(--hfm-space-5);
  color: var(--hfm-color-text-secondary);
  font-size: var(--hfm-text-sm);
  display: grid;
  gap: var(--hfm-space-1);
}

.person-profile__source {
  margin: var(--hfm-space-2) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.recognition-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.recognition-item {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.recognition-item__title {
  margin: 0;
  font-weight: 600;
}

.recognition-item__meta {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-2) var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-azure);
}

.recognition-item__desc {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.achievement-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-1);
}

.achievement-item {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-2) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.achievement-item__title {
  font-weight: 600;
  line-height: var(--hfm-leading-normal);
}

.achievement-item__meta {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-heritage);
  font-variant-numeric: tabular-nums;
}

.achievement-item__desc {
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
  margin: 0;
}

.event-card {
  padding: var(--hfm-space-4) var(--hfm-space-5);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  display: grid;
  gap: var(--hfm-space-1);
}

.event-card__title {
  margin: 0;
  font-family: var(--hfm-font-serif);
  font-weight: 600;
  font-size: var(--hfm-text-lg);
}

.event-card__meta {
  margin: 0;
  color: var(--hfm-color-heritage);
  font-size: var(--hfm-text-sm);
}

.event-card__desc {
  margin: var(--hfm-space-1) 0 0;
  line-height: var(--hfm-leading-reading);
  max-width: 68ch;
}

.event-card__source {
  margin: var(--hfm-space-1) 0 0;
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.studio-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-3);
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.studio-item {
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
  display: grid;
  gap: var(--hfm-space-1);
}

.studio-item__name {
  margin: 0;
  font-weight: 600;
}

.studio-item__institution {
  margin: 0;
  color: var(--hfm-color-heritage);
  font-size: var(--hfm-text-sm);
}

.studio-item__desc {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-muted);
}

.media-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--hfm-space-2);
}

.media-item {
  display: grid;
  gap: var(--hfm-space-1);
  padding: var(--hfm-space-3) var(--hfm-space-4);
  border-bottom: 1px solid var(--hfm-color-border);
}

.media-item__title {
  margin: 0;
  font-weight: 600;
}

.media-item__meta {
  margin: 0;
  color: var(--hfm-color-azure);
  font-size: var(--hfm-text-xs);
}

.media-item__desc {
  margin: 0;
  font-size: var(--hfm-text-sm);
  color: var(--hfm-color-text-secondary);
  line-height: var(--hfm-leading-normal);
  max-width: 68ch;
}

.evidence-note {
  color: var(--hfm-color-text-secondary);
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
}

.heritage-related {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4);
  margin-top: var(--hfm-space-8);
  padding-top: var(--hfm-space-4);
  border-top: 1px solid var(--hfm-color-border);
}

.heritage-related a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
  font-size: var(--hfm-text-sm);
}

.heritage-related a:hover {
  text-decoration: underline;
}

@media (max-width: 767px) {
  .project-profile__row {
    grid-template-columns: 1fr;
    gap: var(--hfm-space-1);
  }

  .person-profile {
    padding: var(--hfm-space-4);
  }
}
</style>
