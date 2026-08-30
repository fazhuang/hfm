<script setup lang="ts">
defineProps<{ label?: string }>()
</script>

<template>
  <div class="state state--empty" role="status">
    <p>{{ label ?? 'No published content available.' }}</p>
  </div>
</template>

<style scoped>
.state {
  padding: var(--hfm-space-6);
  text-align: center;
  color: var(--hfm-color-text-muted);
}
</style>
