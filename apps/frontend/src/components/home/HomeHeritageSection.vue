<script setup lang="ts">
/**
 * HomeHeritageSection — homepage Section 06 (活态传承 / The Living Link, S6-A).
 *
 * CF-09: production visual fidelity for the accepted living-link composition
 * (1440×1240). Proposition: 知识之后，是人 — living transmission in the present.
 * ONE continuous editorial field: DOCUMENTARY ACT (authentic 2023-09-26 师承
 * 教育拜师大会 photograph, materially embedded with edge dissolution) →
 * TRANSMISSION RECORDS (师承教育 principal; 央视《陇脉医承》 / 名中医工作室
 * quieter corroborating records) → HUMAN CARRIER (刘君奇 — continuous register,
 * no cards/chips) → PARTIAL lineage as quiet provenance.
 *
 * TRUTH (CF-09): 刘君奇 = 第六代名医 (customer-confirmed) stays correct; the
 * intermediate lineage gap stays visibly PARTIAL (no fabricated nodes, no
 * completeness claim). The photo is the customer-supplied ceremony asset.
 */
import { HOME_HERITAGE_LIVING, HOME_CHAPTERS } from '../../data/homeProjection'
import { presentationStatusLabel } from '../../presentation/stateMapping'

defineOptions({ name: 'HomeHeritageSection' })

const person = HOME_HERITAGE_LIVING.person
/* PARTIAL lineage via the shared CF-02 mapping — the real, documented
 * completeness signal; never the internal LINEAGE_STRUCTURING marker. */
const lineageLabel = presentationStatusLabel('PARTIAL', '谱系整理中')
/* three documentary traces of living transmission (existing data, in order:
 * 师承教育拜师大会 principal · 央视《陇脉医承》/ 名中医工作室 corroborating). */
const traces = (HOME_HERITAGE_LIVING.traces ?? []).slice(1)
const photo = { src: '/assets/heritage/heritage-baishi-ceremony.jpg', alt: '' }
</script>

<template>
  <section
    id="home-heritage"
    class="home-section home-section--heritage"
    aria-labelledby="home-heritage-title"
  >
    <div class="home-heritage__grain" aria-hidden="true"></div>
    <div class="home-heritage__inner">
      <!-- header -->
      <p class="home-heritage__eyebrow">
        <span class="home-heritage__no">{{ HOME_CHAPTERS.heritage.no }}</span
        >{{ HOME_CHAPTERS.heritage.label }}
      </p>
      <p class="home-heritage__jump">知识，仍在传递</p>

      <div class="home-heritage__head">
        <h2 id="home-heritage-title" class="home-heritage__title">
          {{ HOME_HERITAGE_LIVING.headline }}
        </h2>
        <p class="home-heritage__side">
          皇甫谧针灸以皇甫谧与《针灸甲乙经》为<b>学术源头</b>，是甘肃地域特色的针灸文化传承项目。平台收录其传承人、师承教育、工作室与媒体报道等活态档案。
        </p>
      </div>

      <!-- ONE continuous field: documentary act + transmission records -->
      <div class="home-heritage__field">
        <!-- documentary act — authentic ceremony photo, materially embedded -->
        <figure class="home-heritage__act-pic">
          <img :src="photo.src" alt="" aria-hidden="true" />
          <figcaption class="home-heritage__cap">
            <b>师承教育拜师大会 · 现场</b>2023-09-26 · 甘肃医学院附属医院国医馆 · 客户实拍
          </figcaption>
        </figure>

        <!-- transmission records — 师承教育 principal, the others quieter -->
        <div class="home-heritage__trace" aria-label="传承之实 · 媒体与档案记录">
          <p class="home-heritage__trace-k"><b>传承之实</b><span>同在发生</span></p>
          <div
            v-for="(trace, i) in traces"
            :key="trace.title"
            class="home-heritage__trace-row"
            :class="i === 0 ? 'home-heritage__trace-row--main' : 'home-heritage__trace-row--sub'"
          >
            <p class="home-heritage__trace-t">{{ trace.title }}</p>
            <p class="home-heritage__trace-d">{{ trace.meta }}</p>
          </div>
        </div>
      </div>

      <!-- 刘君奇 — the present human carrier (continuous register, no chips) -->
      <div class="home-heritage__carrier">
        <div class="home-heritage__carrier-row">
          <h3 class="home-heritage__name">{{ person.name }}</h3>
          <p class="home-heritage__role">
            {{ person.generationTitle }} · {{ person.heritageRole }} · {{ person.institutionRole }}
          </p>
        </div>
        <p class="home-heritage__credits">{{ person.professionalTitle }}</p>
        <p class="home-heritage__bio">{{ person.biography }}</p>
        <p class="home-heritage__prov">
          {{ HOME_HERITAGE_LIVING.lineageNote }}
          <span class="home-state-line">
            <span class="hfm-status" data-status="PARTIAL">{{ lineageLabel }}</span>
          </span>
        </p>
      </div>

      <!-- ONE principal CTA -->
      <a class="home-heritage__act" :href="HOME_HERITAGE_LIVING.cta.href"
        ><span class="home-heritage__act-label">{{ HOME_HERITAGE_LIVING.cta.label }}</span>
        <span class="home-heritage__act-arr" aria-hidden="true">→</span></a
      >
    </div>
  </section>
</template>

<style scoped>
/* ===== Section 06 Heritage (The Living Link) — fidelity, 1440×1240 ===== */
.home-section--heritage {
  position: relative;
  overflow: hidden;
  min-height: 1240px;
  margin-inline: calc(-1 * var(--hfm-space-6));
  background:
    radial-gradient(
      1020px 680px at 88% -8%,
      color-mix(in srgb, var(--hfm-color-heritage) 5%, transparent) 0%,
      transparent 62%
    ),
    radial-gradient(
      740px 540px at -4% 114%,
      color-mix(in srgb, var(--hfm-color-accent) 4%, transparent) 0%,
      transparent 60%
    ),
    var(--hfm-color-canvas);
}
.home-heritage__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.home-heritage__inner {
  position: relative;
  max-width: 1272px;
  margin: 0 auto;
  width: 100%;
  height: 1240px;
}

.home-heritage__eyebrow {
  position: absolute;
  left: 0;
  top: 120px;
  font-size: 11px;
  letter-spacing: 0.42em;
  color: var(--hfm-color-heritage);
  margin: 0;
}
.home-heritage__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.home-heritage__jump {
  position: absolute;
  right: 0;
  top: 120px;
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
}
.home-heritage__head {
  position: absolute;
  left: 0;
  top: 188px;
  width: 1120px;
}
.home-heritage__title {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 60px;
  line-height: 1.28;
  letter-spacing: 0.03em;
  color: var(--hfm-color-text);
  margin: 0;
  max-width: 500px;
}
.home-heritage__side {
  margin-top: 26px;
  font-size: 15px;
  line-height: 2.05;
  color: var(--hfm-color-text-secondary);
  max-width: 72ch;
}
.home-heritage__side b {
  color: var(--hfm-color-text);
  font-weight: 600;
}

.home-heritage__field {
  position: absolute;
  left: 0;
  top: 470px;
  width: 1200px;
  height: 480px;
}
.home-heritage__act-pic {
  position: absolute;
  left: 0;
  top: 0;
  width: 730px;
  margin: 0;
  pointer-events: none;
}
.home-heritage__act-pic img {
  width: 730px;
  height: 420px;
  object-fit: cover;
  object-position: center 42%;
  display: block;
  filter: sepia(0.07) saturate(0.9) contrast(1.02);
  -webkit-mask-image:
    linear-gradient(90deg, #000 0, #000 82%, rgba(0, 0, 0, 0) 100%),
    linear-gradient(180deg, #000 0, #000 62%, rgba(0, 0, 0, 0) 100%);
  mask-image:
    linear-gradient(90deg, #000 0, #000 82%, rgba(0, 0, 0, 0) 100%),
    linear-gradient(180deg, #000 0, #000 62%, rgba(0, 0, 0, 0) 100%);
  -webkit-mask-composite: source-in;
  mask-composite: intersect;
}
.home-heritage__cap {
  display: block;
  margin-top: 16px;
  font-size: 11px;
  letter-spacing: 0.06em;
  color: var(--hfm-color-text-muted);
  line-height: 1.8;
  max-width: 600px;
}
.home-heritage__cap b {
  display: block;
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 13px;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.06em;
}

.home-heritage__trace {
  position: absolute;
  right: 0;
  top: 0;
  width: 470px;
}
.home-heritage__trace-k {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 0 0 20px;
  font-size: 11px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
}
.home-heritage__trace-k b {
  font-family: var(--hfm-font-display);
  font-size: 14px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-heritage__trace-row--main {
  padding: 0 0 22px;
}
.home-heritage__trace-row--main .home-heritage__trace-t {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 30px;
  letter-spacing: 0.06em;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-heritage__trace-row--main .home-heritage__trace-d {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.85;
  color: var(--hfm-color-text-secondary);
  max-width: 40ch;
}
.home-heritage__trace-row--main::after {
  content: '';
  display: block;
  margin-top: 22px;
  width: 100%;
  height: 1px;
  background: var(--hfm-color-border);
}
.home-heritage__trace-row--sub {
  padding: 16px 0;
  border-bottom: 1px dotted var(--hfm-color-border);
}
.home-heritage__trace-row--sub:last-child {
  border-bottom: none;
}
.home-heritage__trace-t {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 18px;
  letter-spacing: 0.06em;
  color: var(--hfm-color-text-secondary);
  margin: 0;
}
.home-heritage__trace-d {
  margin-top: 5px;
  font-size: 12px;
  line-height: 1.75;
  color: var(--hfm-color-text-muted);
  max-width: 40ch;
}

.home-heritage__carrier {
  position: absolute;
  left: 0;
  top: 962px;
  width: 1200px;
  border-top: 1px solid var(--hfm-color-border);
  padding-top: 24px;
}
.home-heritage__carrier-row {
  display: flex;
  align-items: baseline;
  gap: 18px;
  flex-wrap: wrap;
}
.home-heritage__name {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 28px;
  letter-spacing: 0.08em;
  color: var(--hfm-color-text);
  margin: 0;
}
.home-heritage__role {
  font-size: 13px;
  letter-spacing: 0.04em;
  color: var(--hfm-color-text-secondary);
  margin: 0;
}
.home-heritage__credits {
  margin-top: 12px;
  font-size: 12px;
  letter-spacing: 0.04em;
  color: var(--hfm-color-text-muted);
}
.home-heritage__bio {
  margin-top: 6px;
  font-size: 12px;
  letter-spacing: 0.03em;
  color: var(--hfm-color-text-secondary);
  line-height: 1.9;
  max-width: 90ch;
}
.home-heritage__prov {
  margin-top: 12px;
  display: flex;
  align-items: baseline;
  gap: 14px;
  flex-wrap: wrap;
  font-size: 11.5px;
  letter-spacing: 0.04em;
  color: var(--hfm-color-text-muted);
  line-height: 1.9;
  max-width: 84ch;
}
.home-state-line {
  display: inline-flex;
}

.home-heritage__act {
  position: absolute;
  right: 0;
  bottom: 52px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 13.5px;
  letter-spacing: 0.18em;
  color: var(--hfm-color-text);
  text-decoration: none;
}
.home-heritage__act-arr {
  color: var(--hfm-color-accent);
  font-family: var(--hfm-font-serif);
  font-size: 15px;
}
.home-heritage__act-label {
  border-bottom: 1px solid var(--hfm-color-border-strong);
  padding-bottom: 4px;
}

/* ===== Responsive (CF-09): reflow below 1200px so no readable content is hidden. ===== */
@media (max-width: 1199px) {
  .home-section--heritage {
    min-height: 0;
    margin-inline: 0;
    padding: 96px 24px 88px;
  }
  .home-heritage__inner {
    height: auto;
    max-width: 720px;
    margin: 0 auto;
  }
  .home-heritage__eyebrow {
    position: static;
    margin: 0;
  }
  .home-heritage__jump {
    position: static;
    margin: 16px 0 0;
    text-align: right;
  }
  .home-heritage__head {
    position: static;
    width: auto;
    margin-top: 60px;
  }
  .home-heritage__title {
    font-size: clamp(30px, 7.6vw, 46px);
    line-height: 1.32;
    max-width: none;
  }
  .home-heritage__side {
    margin-top: 20px;
    font-size: 14px;
    max-width: none;
  }
  .home-heritage__field {
    position: static;
    width: auto;
    height: auto;
    margin-top: 56px;
  }
  .home-heritage__act-pic {
    position: static;
    width: 100%;
    max-width: 720px;
  }
  .home-heritage__act-pic img {
    width: 100%;
    height: auto;
  }
  .home-heritage__cap {
    margin-top: 12px;
    max-width: none;
  }
  .home-heritage__trace {
    position: static;
    width: auto;
    margin-top: 48px;
  }
  .home-heritage__trace-row--main .home-heritage__trace-d,
  .home-heritage__trace-d {
    max-width: none;
  }
  .home-heritage__carrier {
    position: static;
    width: auto;
    margin-top: 56px;
    padding-top: 24px;
  }
  .home-heritage__name {
    font-size: 24px;
  }
  .home-heritage__bio {
    max-width: none;
  }
  .home-heritage__prov {
    max-width: none;
  }
  .home-heritage__act {
    position: static;
    margin-top: 44px;
  }
}
</style>
