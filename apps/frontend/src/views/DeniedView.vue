<script setup lang="ts">
defineOptions({ name: 'DeniedView' })
</script>

<template>
  <section class="denied" aria-labelledby="denied-heading">
    <h1 id="denied-heading">无权限访问</h1>
    <p>当前角色没有访问该页面的权限（默认拒绝）。</p>
    <RouterLink to="/">返回公开门户</RouterLink>
  </section>
</template>
