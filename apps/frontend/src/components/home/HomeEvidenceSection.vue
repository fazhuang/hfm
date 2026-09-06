<script setup lang="ts">
/**
 * HomeEvidenceSection — homepage Section 05 (史料证据 / Evidence S5-C, refined).
 *
 * CF-09: production visual fidelity for the accepted
 * HFM_HOMEPAGE_SECTION05_VISUAL_BASELINE_S5C_REFINED composition (1440×1240).
 * Proposition: 从「说」回到「据」 — every claim must return to its source.
 * ONE scholarly argument held open for inspection: 结论 ↓ 出处 ↓ 争议, causal
 * dependency expressed by indentation/alignment — no arrows/flowcharts/nodes.
 * Provenance register = quiet scholarly marginalia; ONE principal CTA.
 *
 * TRUTH (CF-09): the argument is ONE real witness (房玄龄等《晋书》 quotation,
 * HOME_QUOTATION) plus the documented 建安/正始 dispute; the provenance register
 * derives from the real 其传 · 史料来源整理 document (reader/qichuan). No
 * invented citation totals / repository names / completion percentages.
 */
import { HOME_EVIDENCE, HOME_QUOTATION, HOME_CHAPTERS } from '../../data/homeProjection'

defineOptions({ name: 'HomeEvidenceSection' })

const evidence = HOME_EVIDENCE
const quotation = HOME_QUOTATION

const claim = evidence.claim
const dispute = evidence.dispute
/* Split the dispute text on "正始" to reproduce the accepted azure accent
 * (no new content — the two words come from the frozen projection). */
const disputeParts = dispute.text.split('正始')
const disputeBefore = disputeParts[0] ?? ''
const disputeAfter = disputeParts.slice(1).join('正始')
</script>

<template>
  <section
    id="home-evidence"
    class="home-section home-section--evidence"
    aria-labelledby="home-evidence-title"
  >
    <div class="home-evidence__grain" aria-hidden="true"></div>
    <div class="home-evidence__inner">
      <!-- header -->
      <p class="home-evidence__eyebrow">
        <span class="home-evidence__no">{{ HOME_CHAPTERS.evidence.no }}</span
        >{{ HOME_CHAPTERS.evidence.label }}
      </p>
      <p class="home-evidence__jump">结论 → 出处 → 争议</p>

      <div class="home-evidence__head">
        <h2 id="home-evidence-title" class="home-evidence__title">{{ evidence.headline }}</h2>
        <p class="home-evidence__side">
          平台的判断不替代考证，只呈现考证：结论旁标注依据，争议如实明示。以下为平台已整理的史证材料示例。
        </p>
      </div>

      <!-- ONE scholarly argument held open for inspection -->
      <div class="home-evidence__arg">
        <!-- 01 · CONCLUSION — reduced authority -->
        <div class="home-evidence__st home-evidence__st--1">
          <p class="home-evidence__mar">
            <span class="home-evidence__ord">01</span>{{ claim.label }}
          </p>
          <div class="home-evidence__body">
            <p class="home-evidence__cl">{{ claim.text }}</p>
            <p class="home-evidence__meta">{{ claim.note }}</p>
          </div>
        </div>

        <!-- 02 · SOURCE — the intellectual centre (indented) -->
        <div class="home-evidence__st home-evidence__st--2">
          <p class="home-evidence__mar"><span class="home-evidence__ord">02</span>出处</p>
          <div class="home-evidence__body">
            <p class="home-evidence__src">{{ evidence.sourceLabel }}</p>
            <blockquote class="home-evidence__wit">
              <p class="home-evidence__wit-text">
                <span class="home-evidence__qm">「</span>{{ quotation.text
                }}<span class="home-evidence__qm">」</span>
              </p>
            </blockquote>
            <p class="home-evidence__att">
              <b>{{ quotation.attribution }}</b
              ><span class="home-evidence__dash">—</span
              ><span>{{ quotation.source }} · 后论 / 历史评价</span>
            </p>
          </div>
        </div>

        <!-- 03 · DISPUTE — a qualification of the same argument (indented further) -->
        <div class="home-evidence__st home-evidence__st--3">
          <p class="home-evidence__mar">
            <span class="home-evidence__ord">03</span>{{ dispute.label }}
          </p>
          <div class="home-evidence__body">
            <p class="home-evidence__dis">
              {{ disputeBefore }}<span class="home-evidence__open">正始</span>{{ disputeAfter }}
            </p>
            <p class="home-evidence__q">{{ dispute.note }}</p>
          </div>
        </div>
      </div>

      <!-- PROVENANCE REGISTER — quiet scholarly marginalia (real source types) -->
      <div class="home-evidence__prov" aria-label="出处类型 · 录自其传史料来源整理">
        <p class="home-evidence__prov-k"><b>出处类型</b><span>其传史料来源整理</span></p>
        <div class="home-evidence__reg">
          <p v-for="source in evidence.sources" :key="source.title" class="home-evidence__row">
            <b>{{ source.title }}</b
            ><span class="home-evidence__sep">—</span
            ><a class="home-evidence__src-link" :href="source.href">其传原文 →</a>
          </p>
        </div>
      </div>

      <!-- ONE principal CTA -->
      <a class="home-evidence__act" :href="evidence.cta.href"
        ><span class="home-evidence__act-label">{{ evidence.cta.label }}</span>
        <span class="home-evidence__act-arr" aria-hidden="true">→</span></a
      >
    </div>
  </section>
</template>

<style scoped>
/* ===== Section 05 Evidence (S5-C Refined) — production fidelity, 1440×1240 ===== */
.home-section--evidence {
  position: relative;
  overflow: hidden;
  min-height: 1240px;
  margin-inline: calc(-1 * var(--hfm-space-6));
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
.home-evidence__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.home-evidence__inner {
  position: relative;
  max-width: 1272px;
  margin: 0 auto;
  width: 100%;
  height: 1240px;
}

.home-evidence__eyebrow {
  position: absolute;
  left: 0;
  top: 120px;
  font-size: 11px;
  letter-spacing: 0.42em;
  color: var(--hfm-color-heritage);
  margin: 0;
}
.home-evidence__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.home-evidence__jump {
  position: absolute;
  right: 0;
  top: 120px;
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
}
.home-evidence__head {
  position: absolute;
  left: 0;
  top: 188px;
  width: 1120px;
}
.home-evidence__title {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 60px;
  line-height: 1.28;
  letter-spacing: 0.03em;
  color: var(--hfm-color-text);
  margin: 0;
  max-width: 400px;
}
.home-evidence__side {
  margin-top: 26px;
  font-size: 15px;
  line-height: 2.05;
  color: var(--hfm-color-text-secondary);
  max-width: 70ch;
}

.home-evidence__arg {
  position: absolute;
  left: 0;
  top: 468px;
  width: 840px;
}
.home-evidence__st {
  position: relative;
}
.home-evidence__mar {
  display: flex;
  align-items: baseline;
  gap: 14px;
  font-size: 11px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-heritage);
  margin: 0;
}
.home-evidence__mar::after {
  content: '';
  height: 1px;
  background: var(--hfm-color-border-strong);
  flex: none;
}
.home-evidence__ord {
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.12em;
}

.home-evidence__st--1 {
  left: 0;
}
.home-evidence__st--1 .home-evidence__mar {
  width: 300px;
}
.home-evidence__st--1 .home-evidence__mar::after {
  width: 200px;
}
.home-evidence__body {
  margin-top: 22px;
}
.home-evidence__cl {
  font-family: var(--hfm-font-heading);
  font-size: 30px;
  font-weight: 500;
  letter-spacing: 0.05em;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-evidence__meta {
  margin-top: 12px;
  font-size: 12.5px;
  letter-spacing: 0.05em;
  color: var(--hfm-color-text-muted);
}

.home-evidence__st--2 {
  left: 64px;
  margin-top: 52px;
}
.home-evidence__st--2 .home-evidence__mar {
  width: 360px;
}
.home-evidence__st--2 .home-evidence__mar::after {
  width: 250px;
}
.home-evidence__src {
  font-family: var(--hfm-font-display);
  font-size: 22px;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-evidence__wit {
  margin: 22px 0 0;
}
.home-evidence__wit-text {
  margin: 0;
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 32px;
  line-height: 1.68;
  letter-spacing: 0.02em;
  color: var(--hfm-color-text);
  max-width: 52ch;
}
.home-evidence__qm {
  color: var(--hfm-color-accent);
}
.home-evidence__att {
  margin-top: 20px;
  display: flex;
  align-items: baseline;
  gap: 16px;
  font-size: 13px;
  letter-spacing: 0.06em;
  color: var(--hfm-color-text-secondary);
}
.home-evidence__att b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 15px;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-evidence__dash {
  color: var(--hfm-color-border-strong);
}

.home-evidence__st--3 {
  left: 132px;
  margin-top: 44px;
}
.home-evidence__st--3 .home-evidence__mar {
  width: 400px;
}
.home-evidence__st--3 .home-evidence__mar::after {
  width: 280px;
}
.home-evidence__dis {
  font-family: var(--hfm-font-heading);
  font-size: 29px;
  font-weight: 500;
  letter-spacing: 0.05em;
  color: var(--hfm-color-text-secondary);
  margin: 0;
}
.home-evidence__open {
  color: var(--hfm-color-azure);
}
.home-evidence__q {
  margin-top: 14px;
  font-size: 13px;
  line-height: 1.9;
  color: var(--hfm-color-text-secondary);
  max-width: 58ch;
}

.home-evidence__prov {
  position: absolute;
  right: 0;
  top: 884px;
  width: 340px;
}
.home-evidence__prov-k {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 0 0 14px;
  font-size: 10.5px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
}
.home-evidence__prov-k b {
  font-family: var(--hfm-font-display);
  font-size: 13px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-evidence__reg {
  font-size: 12px;
  letter-spacing: 0.05em;
  color: var(--hfm-color-text-secondary);
  line-height: 2.1;
}
.home-evidence__row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 5px 0;
  margin: 0;
}
.home-evidence__row b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.06em;
  white-space: nowrap;
}
.home-evidence__src-link {
  font-size: 11px;
  color: var(--hfm-color-interactive);
  letter-spacing: 0.02em;
  white-space: nowrap;
}
.home-evidence__sep {
  color: var(--hfm-color-border-strong);
}

.home-evidence__act {
  position: absolute;
  left: 0;
  bottom: 52px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 13.5px;
  letter-spacing: 0.18em;
  color: var(--hfm-color-text);
  text-decoration: none;
}
.home-evidence__act-arr {
  color: var(--hfm-color-accent);
  font-family: var(--hfm-font-serif);
  font-size: 15px;
  transition: transform 0.2s ease;
}
.home-evidence__act:hover .home-evidence__act-arr {
  transform: translateX(4px);
}
.home-evidence__act-label {
  border-bottom: 1px solid var(--hfm-color-border-strong);
  padding-bottom: 4px;
}

/* ===== Responsive (CF-09): reflow below 1200px so no readable content is hidden. ===== */
@media (max-width: 1199px) {
  .home-section--evidence {
    min-height: 0;
    margin-inline: 0;
    padding: 96px 24px 88px;
  }
  .home-evidence__inner {
    height: auto;
    max-width: 720px;
    margin: 0 auto;
  }
  .home-evidence__eyebrow {
    position: static;
    margin: 0;
  }
  .home-evidence__jump {
    position: static;
    margin: 16px 0 0;
    text-align: right;
  }
  .home-evidence__head {
    position: static;
    width: auto;
    margin-top: 60px;
  }
  .home-evidence__title {
    font-size: clamp(30px, 7.6vw, 46px);
    line-height: 1.32;
    max-width: 100%;
  }
  .home-evidence__side {
    margin-top: 20px;
    font-size: 14px;
    max-width: none;
  }
  .home-evidence__arg {
    position: static;
    width: auto;
    margin-top: 60px;
  }
  .home-evidence__st--1,
  .home-evidence__st--2,
  .home-evidence__st--3 {
    left: 0;
    margin-top: 44px;
  }
  .home-evidence__st--1 {
    margin-top: 0;
  }
  .home-evidence__mar {
    width: auto;
  }
  .home-evidence__mar::after {
    width: 110px;
  }
  .home-evidence__cl {
    font-size: 26px;
  }
  .home-evidence__wit {
    margin-top: 20px;
  }
  .home-evidence__wit-text {
    font-size: clamp(21px, 5.6vw, 30px);
    line-height: 1.75;
    max-width: none;
  }
  .home-evidence__att {
    flex-wrap: wrap;
  }
  .home-evidence__q {
    max-width: none;
  }
  .home-evidence__prov {
    position: static;
    width: auto;
    margin-top: 64px;
  }
  .home-evidence__row b {
    white-space: normal;
  }
  .home-evidence__act {
    position: static;
    margin-top: 44px;
  }
}
</style>
