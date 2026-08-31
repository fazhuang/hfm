<script setup lang="ts">
import ExportPanel from '../../components/ExportPanel.vue'

defineOptions({ name: 'ResearchHomeView' })
</script>

<template>
  <section aria-labelledby="research-heading">
    <h1 id="research-heading">研究工作台</h1>
    <p>研究后台基础面：仅限已认证且具备研究角色的用户访问。</p>
    <ExportPanel />
  </section>
</template>
