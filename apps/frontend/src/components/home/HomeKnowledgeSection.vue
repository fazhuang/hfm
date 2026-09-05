<script setup lang="ts">
/**
 * HomeKnowledgeSection — homepage Section 04 (知识对象 / Knowledge S4-B, refined).
 *
 * CF-08: production visual fidelity for the accepted
 * HFM_HOMEPAGE_SECTION04_VISUAL_BASELINE_S4B_REFINED composition (1440×1240).
 * Proposition: a historical work → structured knowledge objects →
 * evidence-backed scholarly exploration. 古籍文字 → 结构化记录 → 可检索知识 →
 * 阅读 / 来源 / 引用. The historical text is the source; the platform turns it
 * into navigable, evidence-backed knowledge — not a generic feature grid.
 *  - header: 04 eyebrow · jump 古籍文字 → 可检索知识 · title · side statement
 *  - transformation zone: manuscript leaf dissolving toward the knowledge
 *    taxonomy (人物/文本/作品 primaries + 版本/档案/论文 layers)
 *  - research path as a scholarly method line (检索→阅读→来源→引用)
 *  - evidence register (quiet numbers) · ONE editorial CTA 进入研究工作台 →
 *
 * TRUTH BOUNDARY (CF-08): every count derives from current data
 * (contentInventory / searchIndex). No invented corpus/entity/citation counts;
 * the taxonomy vocabulary is the platform's real content-type set.
 */
import { HOME_KNOWLEDGE, HOME_CHAPTERS, HOME_RESEARCH_STEPS } from '../../data/homeProjection'

defineOptions({ name: 'HomeKnowledgeSection' })

/* Accepted S4-B split of the six real content types: primary intellectual
 * objects (人物/文本/作品) + evidence/transmission/research layers. */
const primary = HOME_KNOWLEDGE.categories.slice(0, 3)
const layers = HOME_KNOWLEDGE.categories.slice(3)
</script>

<template>
  <section
    id="home-knowledge"
    class="home-section home-section--knowledge"
    aria-labelledby="home-knowledge-title"
  >
    <div class="home-knowledge__grain" aria-hidden="true" />
    <div class="home-knowledge__inner">
      <!-- header -->
      <p class="home-knowledge__eyebrow">
        <span class="home-knowledge__no">{{ HOME_CHAPTERS.knowledge.no }}</span
        >{{ HOME_CHAPTERS.knowledge.label }}
      </p>
      <p class="home-knowledge__jump">古籍文字 → 可检索知识</p>

      <div class="home-knowledge__head">
        <h2 id="home-knowledge-title" class="home-knowledge__title">
          {{ HOME_KNOWLEDGE.headline }}
        </h2>
        <p class="home-knowledge__side">
          《针灸甲乙经》不是一部被「放起来」的古籍。它的<b>篇章、腧穴、经脉、病候与史料依据</b>，正被整理为可检索、可阅读、可回溯出处的知识结构。
        </p>
      </div>

      <!-- transformation zone: manuscript dissolution → structure -->
      <div class="home-knowledge__zone">
        <figure class="home-knowledge__leaf">
          <img src="/assets/jiayi/book-siku-leaf.jpg" alt="" aria-hidden="true" />
          <figcaption class="home-knowledge__leaf-cap">
            <b>《针灸甲乙经》 · 四库全书本</b><br />清乾隆《四库全书》抄本 · 客户资料
          </figcaption>
        </figure>

        <div class="home-knowledge__taxonomy">
          <p class="home-knowledge__tax-heading">
            <b>知识之体</b><span>由文字而出的智识对象</span>
          </p>
          <div class="home-knowledge__prim">
            <div v-for="item in primary" :key="item.title" class="home-knowledge__prim-item">
              <p class="home-knowledge__prim-title">
                {{ item.title }}
              </p>
              <p class="home-knowledge__prim-note">
                {{ item.note }}
              </p>
            </div>
          </div>
          <div class="home-knowledge__layers">
            <p class="home-knowledge__layers-heading">
              <b>证据 · 流传 · 研究</b><span>支撑与延伸层面</span>
            </p>
            <p class="home-knowledge__layers-line">
              <template v-for="(layer, i) in layers" :key="layer.title">
                <b>{{ layer.title }}</b
                >{{ layer.note
                }}<span v-if="i < layers.length - 1" class="home-knowledge__layers-sep">·</span>
              </template>
            </p>
          </div>
        </div>
      </div>

      <!-- research path — a scholarly method line -->
      <div class="home-knowledge__method">
        <p class="home-knowledge__method-heading"><b>研究路径</b><span>从检索到引用</span></p>
        <p class="home-knowledge__method-line">
          <template v-for="(step, i) in HOME_RESEARCH_STEPS" :key="step.label">
            <span class="home-knowledge__step"
              ><b>{{ step.label }}</b
              ><span>{{ step.note }}</span></span
            >
            <span v-if="i < HOME_RESEARCH_STEPS.length - 1" class="home-knowledge__arrow">→</span>
          </template>
        </p>
      </div>

      <!-- evidence register — quiet scholarly numbers (all data-derived) -->
      <div class="home-knowledge__evidence">
        <p class="home-knowledge__evidence-heading">
          <b>平台 · 知识层可检索证据</b>
        </p>
        <p class="home-knowledge__evidence-stats">
          <span class="home-knowledge__stat"
            ><b>{{ HOME_KNOWLEDGE.searchable }}</b
            >条可检索记录 · 统一索引</span
          ><span class="home-knowledge__stat-sep">·</span>
          <span class="home-knowledge__stat"
            ><b>{{ HOME_KNOWLEDGE.categoriesCount }}</b
            >类内容：{{ HOME_KNOWLEDGE.knowledgeTypes }}</span
          ><span class="home-knowledge__stat-sep">·</span>
          <span class="home-knowledge__stat"
            ><b>{{ HOME_KNOWLEDGE.editions }}</b
            >版本记录（《针灸甲乙经》历代版本）</span
          ><span class="home-knowledge__stat-sep">·</span>
          <span class="home-knowledge__stat"
            ><b>{{ HOME_KNOWLEDGE.lunzhu }}</b
            >论著资料（客户资料目录审计）</span
          ><span class="home-knowledge__stat-sep">·</span>
          <span class="home-knowledge__stat"
            ><b>{{ HOME_KNOWLEDGE.lunwen }}</b
            >学术论文（目录审计 · 已结构化题录 {{ HOME_KNOWLEDGE.structured }} 条）</span
          >
        </p>
      </div>

      <!-- ONE editorial CTA -->
      <a class="home-knowledge__act" :href="HOME_KNOWLEDGE.cta.href"
        ><span class="home-knowledge__act-label">{{ HOME_KNOWLEDGE.cta.label }}</span>
        <span class="home-knowledge__act-arr" aria-hidden="true">→</span></a
      >
    </div>
  </section>
</template>

<style scoped>
/* ===== Section 04 Knowledge (S4-B Refined) — fidelity, 1440×1240 ===== */
.home-section--knowledge {
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
      720px 520px at -4% 114%,
      color-mix(in srgb, var(--hfm-color-accent) 4%, transparent) 0%,
      transparent 60%
    ),
    var(--hfm-color-canvas);
}
.home-knowledge__grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.home-knowledge__inner {
  position: relative;
  max-width: 1272px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
}

.home-knowledge__eyebrow {
  position: absolute;
  left: 0;
  top: 120px;
  font-size: 11px;
  letter-spacing: 0.42em;
  color: var(--hfm-color-heritage);
  margin: 0;
}
.home-knowledge__no {
  color: var(--hfm-color-text-muted);
  margin-right: 0.5em;
}
.home-knowledge__jump {
  position: absolute;
  right: 0;
  top: 120px;
  font-size: 12px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
  margin: 0;
}
.home-knowledge__head {
  position: absolute;
  left: 0;
  top: 188px;
  width: 1120px;
}
.home-knowledge__title {
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: 60px;
  line-height: 1.28;
  letter-spacing: 0.03em;
  color: var(--hfm-color-text);
  margin: 0;
  max-width: 11ch;
}
.home-knowledge__side {
  margin-top: 26px;
  font-size: 15px;
  line-height: 2.05;
  color: var(--hfm-color-text-secondary);
  max-width: 70ch;
}
.home-knowledge__side b {
  color: var(--hfm-color-text);
  font-weight: 600;
}

.home-knowledge__zone {
  position: absolute;
  left: 0;
  top: 452px;
  width: 1272px;
  height: 600px;
}
.home-knowledge__leaf {
  position: absolute;
  left: 30px;
  top: 8px;
  width: 270px;
  height: 580px;
  overflow: hidden;
  pointer-events: none;
  opacity: 0.86;
  margin: 0;
}
.home-knowledge__leaf img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 22%;
  filter: sepia(0.16) saturate(0.84) contrast(1.02);
  -webkit-mask-image:
    linear-gradient(90deg, #000 0, #000 38%, rgba(0, 0, 0, 0) 92%),
    linear-gradient(180deg, #000 0, #000 82%, rgba(0, 0, 0, 0) 100%);
  mask-image:
    linear-gradient(90deg, #000 0, #000 38%, rgba(0, 0, 0, 0) 92%),
    linear-gradient(180deg, #000 0, #000 82%, rgba(0, 0, 0, 0) 100%);
  -webkit-mask-composite: source-in;
  mask-composite: intersect;
}
.home-knowledge__leaf-cap {
  position: absolute;
  left: 0;
  top: 596px;
  width: 250px;
  font-size: 10.5px;
  letter-spacing: 0.12em;
  color: var(--hfm-color-text-muted);
}
.home-knowledge__leaf-cap b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 12.5px;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.08em;
}

.home-knowledge__taxonomy {
  position: absolute;
  left: 300px;
  top: 6px;
  width: 900px;
}
.home-knowledge__tax-heading {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 26px;
  font-size: 11px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
}
.home-knowledge__tax-heading b {
  font-family: var(--hfm-font-display);
  font-size: 14px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.1em;
}
.home-knowledge__prim {
  display: flex;
  gap: 60px;
  align-items: baseline;
}
.home-knowledge__prim-item {
  flex: none;
  text-align: left;
}
.home-knowledge__prim-title {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 46px;
  letter-spacing: 0.1em;
  color: var(--hfm-color-text);
}
.home-knowledge__prim-note {
  font-size: 12.5px;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.02em;
  margin-top: 8px;
  max-width: 16ch;
  line-height: 1.7;
}
.home-knowledge__layers {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--hfm-color-border);
}
.home-knowledge__layers-heading {
  font-size: 10.5px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
  margin-bottom: 14px;
}
.home-knowledge__layers-heading b {
  font-family: var(--hfm-font-display);
  font-size: 13px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-knowledge__layers-line {
  font-size: 12.5px;
  letter-spacing: 0.04em;
  color: var(--hfm-color-text-secondary);
  line-height: 2;
}
.home-knowledge__layers-line b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.06em;
  margin-right: 8px;
}
.home-knowledge__layers-sep {
  margin: 0 10px;
  color: var(--hfm-color-border-strong);
}

.home-knowledge__method {
  position: absolute;
  left: 0;
  top: 1058px;
  width: 900px;
  font-size: 13px;
  letter-spacing: 0.03em;
  color: var(--hfm-color-text-secondary);
}
.home-knowledge__method-heading {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 11px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
}
.home-knowledge__method-heading b {
  font-family: var(--hfm-font-display);
  font-size: 14px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-knowledge__method-line {
  display: flex;
  align-items: baseline;
  gap: 16px;
  flex-wrap: nowrap;
  white-space: nowrap;
}
.home-knowledge__step {
  font-size: 13px;
  color: var(--hfm-color-text-secondary);
}
.home-knowledge__step b {
  font-family: var(--hfm-font-display);
  font-size: 17px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-knowledge__step span {
  font-size: 11px;
  color: var(--hfm-color-text-muted);
  letter-spacing: 0.04em;
  margin-left: 8px;
}
.home-knowledge__arrow {
  color: var(--hfm-color-accent);
  font-family: var(--hfm-font-serif);
  font-size: 15px;
}

.home-knowledge__evidence {
  position: absolute;
  left: 0;
  bottom: 96px;
  width: 1272px;
  border-top: 1px solid var(--hfm-color-border);
  padding-top: 18px;
  font-size: 11.5px;
  letter-spacing: 0.05em;
  color: var(--hfm-color-text-muted);
  line-height: 1.9;
}
.home-knowledge__evidence-heading {
  font-size: 10.5px;
  letter-spacing: 0.26em;
  color: var(--hfm-color-text-muted);
  margin-bottom: 8px;
}
.home-knowledge__evidence-heading b {
  font-family: var(--hfm-font-display);
  font-size: 13px;
  font-weight: 500;
  color: var(--hfm-color-text);
  letter-spacing: 0.08em;
}
.home-knowledge__evidence-stats {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
  align-items: baseline;
}
.home-knowledge__stat {
  font-size: 11.5px;
  color: var(--hfm-color-text-muted);
}
.home-knowledge__stat b {
  font-family: var(--hfm-font-display);
  font-weight: 500;
  font-size: 14px;
  color: var(--hfm-color-text-secondary);
  letter-spacing: 0.03em;
  margin-right: 6px;
}
.home-knowledge__stat-sep {
  color: var(--hfm-color-border-strong);
}

.home-knowledge__act {
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
.home-knowledge__act-arr {
  color: var(--hfm-color-accent);
  font-family: var(--hfm-font-serif);
  font-size: 15px;
}
.home-knowledge__act-label {
  border-bottom: 1px solid var(--hfm-color-border-strong);
  padding-bottom: 4px;
}

/* ===== Responsive (CF-08): reflow below 1200px. ===== */
@media (max-width: 1199px) {
  .home-section--knowledge {
    min-height: auto;
    margin-inline: 0;
    padding: var(--hfm-space-12) var(--hfm-space-5);
  }
  .home-knowledge__inner {
    max-width: none;
    height: auto;
  }
  .home-knowledge__eyebrow {
    position: static;
  }
  .home-knowledge__jump {
    position: static;
    margin-top: var(--hfm-space-2);
  }
  .home-knowledge__head {
    position: static;
    width: auto;
  }
  .home-knowledge__title {
    font-size: clamp(32px, 6vw, 60px);
    max-width: none;
  }
  .home-knowledge__side {
    max-width: 46ch;
  }
  .home-knowledge__zone {
    position: static;
    width: auto;
    height: auto;
    margin-top: var(--hfm-space-5);
  }
  .home-knowledge__leaf {
    position: static;
    width: 200px;
    height: 220px;
    margin-bottom: var(--hfm-space-2);
  }
  .home-knowledge__leaf-cap {
    position: static;
    width: auto;
  }
  .home-knowledge__taxonomy {
    position: static;
    width: auto;
    margin-top: var(--hfm-space-4);
  }
  .home-knowledge__prim {
    flex-wrap: wrap;
    gap: 28px;
  }
  .home-knowledge__prim-title {
    font-size: clamp(32px, 6vw, 46px);
  }
  .home-knowledge__method {
    position: static;
    width: auto;
    margin-top: var(--hfm-space-5);
  }
  .home-knowledge__method-line {
    flex-wrap: wrap;
    white-space: normal;
  }
  .home-knowledge__evidence {
    position: static;
    width: auto;
    margin-top: var(--hfm-space-5);
  }
  .home-knowledge__act {
    position: static;
    margin-top: var(--hfm-space-4);
  }
}

@media (max-width: 599px) {
  .home-section--knowledge {
    padding: var(--hfm-space-8) var(--hfm-space-4);
  }
}
</style>
