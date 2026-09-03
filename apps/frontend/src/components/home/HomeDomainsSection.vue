<script setup lang="ts">
/**
 * HomeDomainsSection — accepted homepage Section 07 (Four Domains S7-A Refined).
 *
 * WP-05: production visual fidelity for the frozen
 * HFM_HOMEPAGE_SECTION07_VISUAL_BASELINE_S7A_REFINED composition (1440×1240).
 * Proposition: 叙事之后，是入口 — four content domains as four EDITORIAL
 * THRESHOLDS into ONE platform: 人物档案 / 文献史料 / 医学知识 / 活态传承.
 * Four vertical editorial territories separated by full-height thin scholarly
 * rules; domain material shown as restrained holdings rows; medical numbers as
 * a scholarly bibliographic register (not KPI cards); entry CTAs share ONE
 * navigation grammar anchored to a terminal baseline. No cards / boxes / panels
 * / icons / photography. No "NARRATIVE → USABLE ARCHIVE" copy (removed P2-01).
 *
 * DATA: HOME_DOMAINS.domains (four doors + routes) with supporting holdings
 * selected from existing projections: HOME_HUANGFU.items (person), HOME_LITERATURE
 * .items (archive), HOME_KNOWLEDGE counts 19/92/515 (medicine), HOME_HERITAGE
 * .items + HERITAGE_PERSON (living heritage). Leads are frozen S7-A editorial
 * microcopy. No new domain semantics, no invented facts.
 */
import {
  HOME_DOMAINS,
  HOME_CHAPTERS,
  HOME_HUANGFU,
  HOME_LITERATURE,
  HOME_KNOWLEDGE,
  HOME_HERITAGE,
} from '../../data/homeProjection'

defineOptions({ name: 'HomeDomainsSection' })

const domains = HOME_DOMAINS.domains
/* domain supporting material (existing data, per door) */
const heritageItems = HOME_HERITAGE.items ?? []
const personRows = HOME_HUANGFU.items ?? []
const archiveRows = HOME_LITERATURE.items ?? []
const medicalRows = [
  { value: HOME_KNOWLEDGE.editions, label: '版本记录', note: '历代版本' },
  { value: HOME_KNOWLEDGE.lunzhu, label: '论著资料', note: '件' },
  { value: HOME_KNOWLEDGE.lunwen, label: '学术论文', note: '篇 · 目录审计' },
]
const heritageRows = [
  {
    title: '传承人 · ' + (heritageItems[0]?.title ?? ''),
    meta: heritageItems[0]?.meta ?? '',
  },
  ...heritageItems.slice(1, 3).map((item) => ({ title: item.title, meta: item.meta })),
]
const leads = [
  '从本源史料与后世整理出发，建立皇甫谧的人物档案：其传、其言、后论与生平阶段，均有整理依据可循。',
  '皇甫谧著述与历代相关文献。',
  '围绕一部书的知识体系：版本、脉络、论著与研究。',
  '皇甫谧针灸从文献走入当代课堂与诊室。',
]
</script>

<template>
  <section
    id="home-domains"
    class="home-section home-section--domains"
    aria-labelledby="home-domains-title"
  >
    <div class="home-domains__grain" aria-hidden="true"></div>
    <div class="home-domains__inner">
      <!-- header -->
      <p class="home-eyebrow home-domains__eyebrow">
        <span class="home-eyebrow__no">{{ HOME_CHAPTERS.domains.no }}</span
        >{{ HOME_CHAPTERS.domains.label }}
      </p>

      <div class="home-domains__head">
        <h2 id="home-domains-title" class="home-domains__title">{{ HOME_DOMAINS.headline }}</h2>
        <p class="home-domains__lede"><b>人物 · 文献 · 医学 · 传承</b> —— 四类知识，四个入口。</p>
        <div class="home-domains__rule" aria-hidden="true"></div>
      </div>

      <!-- the four editorial thresholds -->
      <div class="home-domains__thresholds" role="list" aria-label="四域入口">
        <div
          v-for="(domain, i) in domains"
          :key="domain.no"
          class="home-domains__door"
          :class="'home-domains__door--' + domain.no"
          role="listitem"
        >
          <p class="home-domains__no">{{ domain.no }}</p>
          <p class="home-domains__k">{{ domain.key }} · {{ domain.label }}</p>
          <p class="home-domains__t">{{ domain.title }}</p>
          <p class="home-domains__lead">{{ leads[i] }}</p>

          <div class="home-domains__prev">
            <!-- person door: 人物档案 holdings -->
            <template v-if="domain.no === '01'">
              <span v-for="row in personRows" :key="row.title" class="home-domains__pv">
                <b>{{ row.title }}</b
                ><span>{{ row.meta }}</span>
              </span>
            </template>
            <!-- archive door: 文献史料 holdings -->
            <template v-else-if="domain.no === '02'">
              <span v-for="row in archiveRows" :key="row.title" class="home-domains__pv">
                <b>{{ row.title }}</b
                ><span>{{ row.meta }}</span>
              </span>
            </template>
            <!-- medicine door: bibliographic register (19/92/515, not KPI) -->
            <template v-else-if="domain.no === '03'">
              <span class="home-domains__bib">
                <span v-for="row in medicalRows" :key="row.label" class="home-domains__b">
                  <b>{{ row.value }}</b
                  ><span>{{ row.label }} · {{ row.note }}</span>
                </span>
              </span>
            </template>
            <!-- heritage door: living-transmission records -->
            <template v-else>
              <span v-for="row in heritageRows" :key="row.title" class="home-domains__pv">
                <b>{{ row.title }}</b
                ><span>{{ row.meta }}</span>
              </span>
            </template>
          </div>

          <a class="home-domains__go" :href="domain.href"
            ><span class="home-domains__go-u">{{ domain.cta }}</span
            ><span class="home-domains__go-arr">→</span></a
          >
        </div>
      </div>

      <div class="home-domains__foot" aria-hidden="true">
        <span class="home-domains__foot-cap">四域 · 四入口 · 一平台</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ===== Section 07 Domains (S7-A Refined) — production fidelity, 1440×1240 ===== */
.home-section--domains {
  position: relative;
  overflow: hidden;
  min-height: 1240px;
  background:
    radial-gradient(
      1040px 680px at 88% -8%,
      color-mix(in srgb, var(--hfm-color-heritage) 5%, transparent) 0%,
      transparent 62%
    ),
    radial-gradient(
      760px 540px at -4% 114%,
      color-mix(in srgb, var(--hfm-color-accent) 4%, transparent) 0%,
      transparent 60%
    ),
    var(--hfm-color-canvas);
}
.home-domains__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.home-domains__inner {
  position: relative;
  max-width: 1272px;
  margin: 0 auto;
  width: 100%;
  height: 1240px;
}

/* header */
.home-domains__eyebrow {
  position: absolute;
  left: 0;
  top: 120px;
  margin: 0;
}
.home-domains__head {
  position: absolute;
  left: 0;
  top: 176px;
  width: 1200px;
}
.home-domains__title {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 66px;
  line-height: 1.22;
  letter-spacing: 0.03em;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-domains__lede {
  margin-top: 24px;
  font-size: 15px;
  letter-spacing: 0.14em;
  color: var(--hfm-color-text-muted);
}
.home-domains__lede b {
  color: var(--hfm-color-text);
  font-weight: 500;
  letter-spacing: 0.02em;
}
.home-domains__rule {
  margin-top: 34px;
  width: 100%;
  height: 1px;
  background: var(--hfm-color-border);
}

/* the four thresholds — vertical rules as architectural continuity */
.home-domains__thresholds {
  position: absolute;
  left: 0;
  top: 400px;
  width: 1200px;
  height: 716px;
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}
.home-domains__door {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 6px 40px 0;
  text-align: left;
}
.home-domains__door:first-child {
  padding-left: 0;
}
.home-domains__door:last-child {
  padding-right: 0;
}
/* asymmetric weight — the person realm reads as the first threshold */
.home-domains__door--01 {
  flex: 1.35;
}
.home-domains__door + .home-domains__door::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--hfm-color-border);
}
.home-domains__no {
  font-family: var(--hfm-font-heading);
  font-size: 20px;
  font-weight: 500;
  color: var(--hfm-color-heritage);
  margin: 0;
}
.home-domains__k {
  margin-top: 14px;
  font-size: 11px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
  margin: 14px 0 0;
}
.home-domains__t {
  margin: 12px 0 0;
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  line-height: 1.16;
  letter-spacing: 0.04em;
  color: var(--hfm-color-text);
}
.home-domains__door--01 .home-domains__t {
  font-size: 42px;
}
.home-domains__door--02 .home-domains__t,
.home-domains__door--04 .home-domains__t {
  font-size: 33px;
}
.home-domains__door--03 .home-domains__t {
  font-size: 34px;
}
.home-domains__lead {
  margin: 16px 0 0;
  font-size: 13px;
  line-height: 1.9;
  color: var(--hfm-color-text-secondary);
  max-width: 34ch;
}

/* domain material — the holdings inside each territory */
.home-domains__prev {
  margin-top: 22px;
  display: block;
}
.home-domains__pv {
  display: block;
  padding: 9px 0;
  border-top: 1px dotted var(--hfm-color-border);
  font-size: 12px;
  color: var(--hfm-color-text-muted);
  margin: 0;
}
.home-domains__pv b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 14px;
  color: var(--hfm-color-text);
  letter-spacing: 0.04em;
  display: block;
}
.home-domains__pv span {
  font-size: 11px;
  color: var(--hfm-color-text-muted);
  letter-spacing: 0.03em;
  display: block;
  margin-top: 3px;
}
/* medical numbers — a scholarly bibliographic register (not KPI) */
.home-domains__bib {
  display: block;
  margin-top: 22px;
  font-size: 11px;
  letter-spacing: 0.03em;
  color: var(--hfm-color-text-muted);
  line-height: 2.05;
}
.home-domains__b {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 0;
  border-top: 1px dotted var(--hfm-color-border);
}
.home-domains__b:last-child {
  border-bottom: 1px dotted var(--hfm-color-border);
}
.home-domains__b b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 15px;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.02em;
}
.home-domains__b span {
  font-size: 11px;
  color: var(--hfm-color-text-muted);
  letter-spacing: 0.04em;
}

/* entry CTA — shared navigation grammar, anchored to the terminal baseline */
.home-domains__go {
  margin-top: auto;
  padding-top: 34px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 13.5px;
  letter-spacing: 0.18em;
  color: var(--hfm-color-text);
  text-decoration: none;
  align-self: flex-start;
}
.home-domains__go-arr {
  color: var(--hfm-color-accent);
  font-family: var(--hfm-font-serif);
  font-size: 15px;
}
.home-domains__go-u {
  border-bottom: 1px solid var(--hfm-color-border-strong);
  padding-bottom: 4px;
}

/* bottom register — editorial closure */
.home-domains__foot {
  position: absolute;
  left: 0;
  bottom: 54px;
  width: 1200px;
  height: 1px;
  background: var(--hfm-color-border);
}
.home-domains__foot-cap {
  position: absolute;
  right: 0;
  bottom: 20px;
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--hfm-color-text-muted);
}

/* ===== Mobile flow (max-width 1199px) — all four thresholds reachable ===== */
@media (max-width: 1199px) {
  .home-section--domains {
    min-height: 0;
    padding: 96px 24px 88px;
  }
  .home-domains__inner {
    height: auto;
    max-width: 720px;
    margin: 0 auto;
  }
  .home-domains__eyebrow {
    position: static;
    margin: 0;
  }
  .home-domains__head {
    position: static;
    width: auto;
    margin-top: 60px;
  }
  .home-domains__title {
    font-size: clamp(34px, 9.5vw, 56px);
  }
  .home-domains__lede {
    font-size: 14px;
    letter-spacing: 0.08em;
    line-height: 1.9;
  }
  .home-domains__rule {
    margin-top: 28px;
  }
  .home-domains__thresholds {
    position: static;
    width: auto;
    height: auto;
    margin-top: 48px;
    flex-direction: column;
    gap: 0;
  }
  .home-domains__door {
    flex: none;
    width: auto;
    padding: 0 0 40px;
  }
  .home-domains__door--01 {
    flex: none;
  }
  .home-domains__door + .home-domains__door {
    padding-top: 40px;
    border-top: 1px solid var(--hfm-color-border);
  }
  .home-domains__door + .home-domains__door::before {
    display: none;
  }
  .home-domains__door .home-domains__t {
    font-size: clamp(27px, 7vw, 36px);
  }
  .home-domains__lead {
    max-width: none;
  }
  .home-domains__prev {
    margin-top: 20px;
  }
  .home-domains__pv span,
  .home-domains__b span {
    white-space: normal;
  }
  .home-domains__go {
    margin-top: 30px;
    padding-top: 0;
    align-self: flex-start;
  }
  .home-domains__foot {
    position: static;
    width: auto;
    margin-top: 56px;
    height: auto;
    background: none;
    border-top: 1px solid var(--hfm-color-border);
  }
  .home-domains__foot-cap {
    position: static;
    display: block;
    text-align: right;
    margin-top: 14px;
  }
}

</style>
