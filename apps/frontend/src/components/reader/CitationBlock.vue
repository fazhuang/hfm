<script setup lang="ts">
/**
 * CitationBlock — deterministic citation display + copy (UI-07).
 *
 * Citation granularity stays at the real source level (no invented 卷/页/版本号).
 * Copy produces a deterministic plain-text citation.
 */
import { ref } from 'vue'

defineOptions({ name: 'CitationBlock' })

const props = defineProps<{
  title: string
  attribution?: string
  work?: string
  section?: string
  source: string
}>()

const copied = ref(false)

function citationText(): string {
  const parts = [props.title]
  if (props.work) parts.push(`作品：${props.work}`)
  if (props.section) parts.push(`章节：${props.section}`)
  if (props.attribution) parts.push(`出处：${props.attribution}`)
  parts.push(`来源：${props.source}`)
  parts.push('—— 皇甫谧人文数字平台（非商业公益性平台）')
  return parts.join('\n')
}

async function onCopy(): Promise<void> {
  try {
    const clipboard = typeof window !== 'undefined' ? window.navigator?.clipboard : undefined
    if (clipboard) {
      await clipboard.writeText(citationText())
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
    }
  } catch {
    // clipboard unavailable (e.g. non-secure context): no-op fallback
    copied.value = false
  }
}
</script>

<template>
  <figure class="citation">
    <blockquote class="citation__quote">
      <slot />
    </blockquote>
    <figcaption class="citation__meta">
      <span v-if="work" class="citation__item">作品：{{ work }}</span>
      <span v-if="section" class="citation__item">章节：{{ section }}</span>
      <span v-if="attribution" class="citation__item">出处：{{ attribution }}</span>
      <span class="citation__item">来源：{{ source }}</span>
    </figcaption>
    <button type="button" class="citation__copy" :aria-label="`复制引用：${title}`" @click="onCopy">
      {{ copied ? '已复制' : '复制引用' }}
    </button>
  </figure>
</template>

<style scoped>
.citation {
  margin: var(--hfm-space-4) 0;
  padding: var(--hfm-space-4) var(--hfm-space-5);
  border-left: 3px solid var(--hfm-color-citation);
  background: var(--hfm-color-surface);
  border-radius: var(--hfm-radius-sm);
}

.citation__quote {
  margin: 0 0 var(--hfm-space-2);
  font-family: var(--hfm-font-serif);
  line-height: var(--hfm-leading-reading);
  color: var(--hfm-color-text);
}

.citation__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-1) var(--hfm-space-4);
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.citation__copy {
  margin-top: var(--hfm-space-2);
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-citation);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-citation);
  cursor: pointer;
  font-size: var(--hfm-text-sm);
}
</style>
