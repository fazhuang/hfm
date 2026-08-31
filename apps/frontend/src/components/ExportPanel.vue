<script setup lang="ts">
import { ref } from 'vue'
import { exportMarkdown, exportPrint, type ExportRecord } from '../services/export'

defineOptions({ name: 'ExportPanel' })

const record: ExportRecord = {
  title: '《针灸甲乙经》校勘笔记',
  body: '卷一引文与校勘说明。',
  publicationState: 'published',
}

const output = ref<string | null>(null)

function onExportMarkdown(): void {
  output.value = exportMarkdown(record)
}

function onExportPrint(): void {
  output.value = exportPrint(record)
}
</script>

<template>
  <section class="export-panel" aria-labelledby="export-heading">
    <h2 id="export-heading">导出</h2>
    <div class="export-panel__actions">
      <button type="button" @click="onExportMarkdown">导出 Markdown</button>
      <button type="button" @click="onExportPrint">打印视图</button>
    </div>
    <pre v-if="output" class="export-panel__output" data-testid="export-output">{{ output }}</pre>
  </section>
</template>

<style scoped>
/* P2-06 print styles: the print artifact is plain text with the disclaimer. */
.export-panel__output {
  white-space: pre-wrap;
  border: 1px solid var(--hfm-color-border);
  border-radius: var(--hfm-radius-md);
  padding: var(--hfm-space-4);
  background: var(--hfm-color-surface);
}

@media print {
  .export-panel__actions {
    display: none;
  }
}
</style>
