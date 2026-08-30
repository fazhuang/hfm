<script setup lang="ts">
defineProps<{ label?: string }>()
</script>

<template>
  <div role="status" aria-live="polite" class="state state--loading">
    <p>{{ label ?? 'Loading…' }}</p>
  </div>
</template>

<style scoped>
.state {
  padding: var(--hfm-space-6);
  text-align: center;
  color: var(--hfm-color-text-muted);
}
</style>
