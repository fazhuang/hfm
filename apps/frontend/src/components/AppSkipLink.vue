<script setup lang="ts">
/**
 * AppSkipLink — keyboard users jump straight to main content (P10).
 * Visually hidden until focused; target = the layout's #main-content.
 */
defineOptions({ name: 'AppSkipLink' })
</script>

<template>
  <a class="skip-link" href="#main-content">跳到主内容</a>
</template>

<style scoped>
.skip-link {
  position: absolute;
  left: var(--hfm-space-2);
  top: -100%;
  z-index: 100;
  padding: var(--hfm-space-2) var(--hfm-space-4);
  background: var(--hfm-color-surface);
  border: 1px solid var(--hfm-color-border-strong);
  border-radius: var(--hfm-radius-sm);
  color: var(--hfm-color-text);
  text-decoration: none;
}

.skip-link:focus-visible {
  top: var(--hfm-space-2);
}
</style>
