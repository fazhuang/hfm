<script setup lang="ts">
/**
 * EditionLineageImage — UI-08 version-lineage visual (customer PNG asset).
 *
 * The customer-provided lineage PNG is a public presentation asset. It is
 * displayed with caption + source; a keyboard-accessible enlarge dialog
 * (focus trap, ESC close, focus return, reduced-motion safe). The image is
 * NOT a pure background; alt carries meaning. Structured edition relations
 * remain [DATA-GAP: JIAYI_EDITION_RELATIONS] — the PNG is never
 * reconstructed into formal genealogical edges.
 */
import { onBeforeUnmount, ref } from 'vue'
import { useFocusTrap } from '../../composables/useFocusTrap'
import {
  JIAYI_LINEAGE_IMAGE_ALT,
  JIAYI_LINEAGE_IMAGE_SRC,
  JIAYI_PUBLIC_SOURCES,
} from '../../data/jiayiView'

defineOptions({ name: 'EditionLineageImage' })

const open = ref(false)
const triggerRef = ref<{ focus(): void } | null>(null)
const { containerRef: dialogRef, activate, deactivate } = useFocusTrap()

function openDialog(): void {
  open.value = true
  activate()
  document.addEventListener('keydown', onGlobalKeydown)
}

function closeDialog(): void {
  if (!open.value) return
  open.value = false
  deactivate(triggerRef.value)
  document.removeEventListener('keydown', onGlobalKeydown)
}

function onGlobalKeydown(event: { key: string }): void {
  if (event.key === 'Escape') {
    closeDialog()
  }
}

onBeforeUnmount(() => {
  deactivate()
  document.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<template>
  <figure class="lineage">
    <img class="lineage__img" :src="JIAYI_LINEAGE_IMAGE_SRC" :alt="JIAYI_LINEAGE_IMAGE_ALT" />
    <figcaption class="lineage__caption">
      <span class="lineage__title">《针灸甲乙经》版本脉络图</span>
      <span class="lineage__note">{{ JIAYI_PUBLIC_SOURCES.lineage }}</span>
      <span class="lineage__data-gap">
        图中关系为资料示意；结构化版本关系尚未建模（DATA-GAP），不据此推断版本继承关系。
      </span>
    </figcaption>
    <button
      ref="triggerRef"
      type="button"
      class="lineage__enlarge"
      aria-haspopup="dialog"
      @click="openDialog"
    >
      查看大图
    </button>
  </figure>

  <div
    v-if="open"
    ref="dialogRef"
    class="lineage-dialog"
    role="dialog"
    aria-modal="true"
    aria-labelledby="lineage-dialog-title"
    tabindex="-1"
  >
    <div class="lineage-dialog__frame">
      <h2 id="lineage-dialog-title" class="lineage-dialog__title">《针灸甲乙经》版本脉络图</h2>
      <img
        class="lineage-dialog__img"
        :src="JIAYI_LINEAGE_IMAGE_SRC"
        :alt="JIAYI_LINEAGE_IMAGE_ALT"
      />
      <button type="button" class="lineage-dialog__close" @click="closeDialog">关闭（Esc）</button>
    </div>
  </div>
</template>

<style scoped>
.lineage {
  margin: 0;
  padding: var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.lineage__img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: var(--hfm-radius-sm);
}

.lineage__caption {
  margin-top: var(--hfm-space-3);
  display: grid;
  gap: var(--hfm-space-1);
}

.lineage__title {
  font-family: var(--hfm-font-serif);
  font-weight: 600;
}

.lineage__note,
.lineage__data-gap {
  font-size: var(--hfm-text-xs);
  color: var(--hfm-color-text-muted);
}

.lineage__data-gap {
  color: var(--hfm-color-warning);
}

.lineage__enlarge {
  margin-top: var(--hfm-space-3);
  padding: var(--hfm-space-1) var(--hfm-space-3);
  border: 1px solid var(--hfm-color-accent);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-accent);
  cursor: pointer;
}

.lineage-dialog {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: var(--hfm-space-6);
  background: rgba(31, 26, 22, 0.72);
}

.lineage-dialog__frame {
  max-width: min(96vw, 1200px);
  max-height: 92vh;
  overflow: auto;
  padding: var(--hfm-space-4);
  border-radius: var(--hfm-radius-md);
  background: var(--hfm-color-surface);
}

.lineage-dialog__title {
  margin: 0 0 var(--hfm-space-3);
  font-size: var(--hfm-text-lg);
}

.lineage-dialog__img {
  display: block;
  max-width: 100%;
  height: auto;
}

.lineage-dialog__close {
  margin-top: var(--hfm-space-3);
  padding: var(--hfm-space-1) var(--hfm-space-4);
  border: 1px solid var(--hfm-color-border-strong);
  border-radius: var(--hfm-radius-sm);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text);
  cursor: pointer;
}
</style>
