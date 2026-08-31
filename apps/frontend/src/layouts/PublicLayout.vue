<script setup lang="ts">
import { RouterView } from 'vue-router'

defineOptions({ name: 'PublicLayout' })
</script>

<template>
  <div class="public-shell">
    <header class="public-shell__header">
      <a class="public-shell__brand" href="/">HFM · 皇甫谧人文数字平台</a>
      <nav class="public-shell__nav" aria-label="Public navigation">
        <a href="/">首页</a>
        <a href="/reader">阅读</a>
        <a href="/search">检索</a>
        <a href="/heritage">传承</a>
        <a href="/library">资料库</a>
        <a href="/login">登录</a>
      </nav>
    </header>
    <main class="public-shell__main">
      <RouterView />
    </main>
    <footer class="public-shell__footer">
      <p>公开门户 · 仅展示已获准发布内容</p>
    </footer>
  </div>
</template>

<style scoped>
.public-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.public-shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--hfm-space-4);
  padding: var(--hfm-space-4) var(--hfm-space-6);
  border-bottom: 1px solid var(--hfm-color-border);
  background: var(--hfm-color-surface);
}

.public-shell__brand {
  font-weight: 600;
  color: var(--hfm-color-text);
  text-decoration: none;
}

.public-shell__nav {
  display: flex;
  gap: var(--hfm-space-4);
}

.public-shell__nav a {
  color: var(--hfm-color-accent);
  text-decoration: none;
}

.public-shell__main {
  flex: 1;
  padding: var(--hfm-space-6);
}

.public-shell__footer {
  padding: var(--hfm-space-4) var(--hfm-space-6);
  border-top: 1px solid var(--hfm-color-border);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
}

@media (max-width: 767px) {
  .public-shell__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
