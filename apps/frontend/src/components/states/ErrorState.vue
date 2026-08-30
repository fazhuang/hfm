<script setup lang="ts">
defineProps<{ message?: string }>()
</script>

<template>
  <div class="state state--error" role="alert">
    <p>{{ message ?? 'Something went wrong loading public content.' }}</p>
  </div>
</template>

<style scoped>
.state {
  padding: var(--hfm-space-6);
  text-align: center;
  color: var(--hfm-color-danger);
}
</style>
