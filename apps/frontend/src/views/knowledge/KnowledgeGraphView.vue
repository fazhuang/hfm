<script setup lang="ts">
/**
 * KnowledgeGraphView — 栏目页「知识图谱」(/knowledge)。
 *
 * HFM-UI-CONTRACT-v2 §3.2 栏目页骨架。内容是**真实已发布投影**：
 * `/api/v1/public/c-terms` 的 30 条经穴 / 经脉 / 病症 / 治法术语。
 *
 * 图谱可视化（实体网络图）本轮**未建** —— 库内 `relations` 只有 5 条，
 * 画成图只会是一片离散的点。页面上如实说明，不画一张空图充数（契约 §5.6）。
 */
import { computed, onMounted, ref } from 'vue'
import { publicGet } from '../../services/api'

defineOptions({ name: 'KnowledgeGraphView' })

interface CTerm {
  entity_id: string
  term_type: string
  term_name: string
  publication_status: string
}

const TYPE_LABELS: Record<string, { zh: string; en: string; note: string }> = {
  acupoint: { zh: '经穴', en: 'ACUPOINT', note: '《针灸甲乙经》所载穴位名。' },
  meridian: { zh: '经脉', en: 'MERIDIAN', note: '十二经脉与奇经八脉名。' },
  disease_symptom: { zh: '病症', en: 'DISEASE', note: '书中主治的病症与证候名。' },
  technique: { zh: '治法', en: 'TECHNIQUE', note: '刺法、灸法等施治技术名。' },
}

const terms = ref<CTerm[]>([])
const loaded = ref(false)
const failed = ref(false)

onMounted(async () => {
  try {
    const res = await publicGet<{ terms: CTerm[]; total: number }>('/api/v1/public/c-terms')
    terms.value = res.terms ?? []
  } catch {
    failed.value = true
  } finally {
    loaded.value = true
  }
})

/** 按类分组，顺序固定，空类不渲染。 */
const groups = computed(() => {
  const order = ['acupoint', 'meridian', 'disease_symptom', 'technique']
  return order
    .map((type) => ({
      type,
      meta: TYPE_LABELS[type] ?? { zh: type, en: type.toUpperCase(), note: '' },
      items: terms.value.filter((t) => t.term_type === type),
    }))
    .filter((g) => g.items.length > 0)
})
</script>

<template>
  <div class="page">
    <section class="pg-hero">
      <div class="xl-inner">
        <p class="xl-label">KNOWLEDGE GRAPH</p>
        <h1 class="pg-hero__title">知识图谱</h1>
        <p class="pg-hero__rule" aria-hidden="true"></p>
        <p class="pg-hero__lede">
          把典籍读成一张关系网 —— 穴位、经脉、病症与治法，在这里各自成为可检索的知识实体。
        </p>
      </div>
    </section>

    <section class="xl-sec" aria-labelledby="kg-terms-title">
      <div class="xl-inner">
        <header class="xl-head">
          <div class="xl-head__aside">
            <span class="xl-index">01</span>
            <span class="xl-label">ENTITIES</span>
          </div>
          <div>
            <h2 id="kg-terms-title" class="xl-title">已发布知识实体</h2>
            <p class="xl-lede">
              共 <span class="xl-num xl-mark">{{ terms.length }}</span> 条，全部来自已发布投影。
            </p>
          </div>
        </header>

        <p v-if="!loaded" class="pg-state">正在读取已发布投影…</p>
        <p v-else-if="failed" class="pg-state">暂时无法读取知识实体，请稍后再试。</p>
        <p v-else-if="groups.length === 0" class="pg-state">知识实体尚未发布。</p>

        <div v-else class="kg-groups">
          <section v-for="g in groups" :key="g.type" class="kg-group">
            <h3 class="kg-group__title">
              {{ g.meta.zh }}
              <span class="kg-group__en">{{ g.meta.en }}</span>
              <span class="xl-num xl-mark kg-group__count">{{ g.items.length }}</span>
            </h3>
            <p class="kg-group__note">{{ g.meta.note }}</p>
            <ul class="kg-terms">
              <li v-for="t in g.items" :key="t.entity_id" class="kg-term">
                {{ t.term_name }}
              </li>
            </ul>
          </section>
        </div>

        <p class="kg-note">
          实体之间的关系（师承、著作、版本脉络）尚在整理，图谱视图待其成型后开放。
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page {
  background: var(--wl-paper);
  color: var(--wl-ink);
}

/* 栏目页首屏与状态行的版式在 styles/home-scale.css 的「栏目页首屏」段，全站共用。 */

.kg-groups {
  display: grid;
  gap: clamp(2rem, 4vw, 3rem);
}
.kg-group__title {
  display: flex;
  align-items: baseline;
  gap: var(--hfm-space-4);
  margin: 0;
  padding-bottom: var(--hfm-space-3);
  border-bottom: 1px solid var(--wl-rule);
  font-family: var(--hfm-font-heading);
  font-weight: 500;
  font-size: var(--hfm-text-xl);
  color: var(--wl-ink);
}
.kg-group__en {
  font-family: var(--wl-latin);
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 0.625rem;
  color: var(--wl-mute);
}
.kg-group__count {
  margin-left: auto;
  font-size: var(--hfm-text-base);
}
.kg-group__note {
  margin: var(--hfm-space-3) 0 var(--hfm-space-5);
  font-size: var(--hfm-text-sm);
  line-height: 1.8;
  color: var(--wl-mute);
}
.kg-terms {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-3);
  margin: 0;
  padding: 0;
  list-style: none;
}
.kg-term {
  padding: 0.35rem 0.85rem;
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-base);
  color: var(--wl-ink-2);
  border: 1px solid var(--wl-rule);
  border-radius: 2px;
}

.kg-note {
  margin: clamp(2.5rem, 5vw, 3.5rem) 0 0;
  padding-top: var(--hfm-space-5);
  border-top: 1px solid var(--wl-rule);
  font-size: var(--hfm-text-sm);
  line-height: 1.9;
  color: var(--wl-mute);
}
</style>
